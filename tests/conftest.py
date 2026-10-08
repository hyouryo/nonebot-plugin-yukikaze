"""pytest 全局配置。

关键点一：插件必须在**测试模块 import 之前**加载好。
测试文件会 ``from nonebot_plugin_yukikaze import ...``，而包在 import 时就会
注册事件响应器（``on_command`` / ``on_notice`` 需要已初始化的 driver）。
如果把这步放进 fixture，收集阶段就会先撞上
``ValueError: NoneBot has not been initialized``。

关键点二：临时目录。pytest 的临时根默认落在系统 temp，受限环境下不一定可写。
这里不回退用 ``--basetemp`` / ``PYTEST_DEBUG_TEMPROOT``，因为 pytest 会在目标
目录下建 ``pytest-of-*`` 再做 ``scandir`` 回收，受限环境下这一步会被拒绝并让
xdist 直接 ``INTERNALERROR``。改成自带 ``tmp_path`` fixture：只创建、只访问
自己这一层的目录，不触碰 pytest 的回收逻辑。
"""

import os
import uuid
from pathlib import Path
from collections.abc import Iterator

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

if (_PROJECT_ROOT / ".env.dev").exists():
    os.environ["ENVIRONMENT"] = "dev"
else:
    os.environ["ENVIRONMENT"] = "test"

import nonebot
from pytest_asyncio import is_async_test
from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

nonebot.init()
nonebot.get_driver().register_adapter(OnebotV11Adapter)
# 照 pyproject.toml 的 [tool.nonebot.plugins] 加载被测试的插件。
# 用绝对路径：pytest 可能从别的目录被调用（IDE 常见），相对路径会找不到文件。
nonebot.load_from_toml(str(_PROJECT_ROOT / "pyproject.toml"))


def pytest_collection_modifyitems(items: list[pytest.Item]):
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


@pytest.fixture
def capture_send(monkeypatch: pytest.MonkeyPatch):
    """替换 ``Bot.send``，把 handler 真正发出去的消息原样记下来。

    nonebug 的 ``should_call_send`` 会对消息做一次类型转换再比较，随机内容
    （随机文案、随机表情包）很难用它做确定性断言；而且在 ``async with`` 块内
    读不到队列（事件是在 ``__aexit__`` 里才处理的）。这个 fixture 绕开这两点。

    用法::

        async with app.test_matcher(matcher) as ctx:
            bot = ctx.create_bot(base=Bot, adapter=adapter)
            captured = capture_send(bot)
            ctx.receive_event(bot, event)
            ctx.should_finished()

        assert captured.message == ...
    """
    captured: list[tuple[object, dict]] = []

    async def fake_send(self, event, message=None, **kwargs):
        captured.append((message, kwargs))
        return None

    class Capture:
        @property
        def message(self):
            assert captured, "handler 没有发送任何消息"
            return captured[-1][0]

        @property
        def kwargs(self) -> dict:
            assert captured, "handler 没有发送任何消息"
            return captured[-1][1]

    def install(bot) -> Capture:
        monkeypatch.setattr(bot, "send", fake_send.__get__(bot, type(bot)))
        return Capture()

    return install


@pytest.fixture
def tmp_path(request: pytest.FixtureRequest) -> Iterator[Path]:
    """替代内置 ``tmp_path``：落在工作区内，绕开系统 temp 的权限限制。

    每个测试独占一个目录，``exist_ok=True`` 兼容别的 worker 先建好这一层的情况。
    **不要**再加一个「会话结束时删掉整个 .pytest_tmp」的 fixture：xdist 下每个
    worker 都会跑会话级 fixture，先跑完的 worker 会把其他 worker 正在用的目录
    一起删掉。这里只清理自己那一个目录，并且只有当它确实是空的时候才顺手删掉
    自己和根目录——「最后一个走的关灯」。
    """
    worker = os.environ.get("PYTEST_XDIST_WORKER", "gw0")
    tmp_root = Path(".pytest_tmp")
    root = tmp_root / worker / f"{request.node.name}-{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    yield root
    # 目录里可能有残留文件，尽力清理，失败也不影响测试结论
    import shutil

    shutil.rmtree(root, ignore_errors=True)

    # 先收空的 worker 层，再收空的根目录；非空说明别的 worker 还在用，跳过
    for directory in (root.parent, tmp_root):
        try:
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()
        except OSError:
            # 并行时可能被另一个进程同时收掉，忽略即可
            pass
