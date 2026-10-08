"""`雪风帮助` 命令：文案由已加载子插件的元数据拼成。"""

import pytest
from nonebug import App

from tests.fake import fake_group_message_event_v11


@pytest.mark.asyncio
@pytest.mark.parametrize("trigger", ["雪风帮助", "帮助"])
async def test_help_replies_with_feature_list(app: App, trigger: str, capture_send):
    """别名「帮助」与原命令等价，回复的都是当前功能列表。"""
    import nonebot
    from nonebot.adapters.onebot.v11 import Bot, Adapter, Message

    from nonebot_plugin_yukikaze import help_cmd, _help_text

    event = fake_group_message_event_v11(message=Message(trigger))

    async with app.test_matcher(help_cmd) as ctx:
        adapter = nonebot.get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        captured = capture_send(bot)
        ctx.receive_event(bot, event)
        ctx.should_finished()

    assert str(captured.message) == _help_text()


def test_help_text_mentions_every_sub_plugin():
    """帮助文案覆盖三个子插件，顺序固定为 _sub_plugins 里的声明顺序。"""
    from nonebot_plugin_yukikaze import _help_text

    text = _help_text()

    assert text.startswith("雪风帮助")
    body = text.split("\n", 1)[1].splitlines()
    assert len(body) == 3
    assert [line.split("：")[0].removeprefix("· ") for line in body] == [
        "poke",
        "get_song",
        "no_talking_laughing",
    ]
    # 每行都带上了子插件的 usage，而不是一句会过期的硬编码文案
    assert all("：" in line and line.split("：", 1)[1] for line in body)

    # 确定性：重复调用结果一致
    assert text == _help_text()
