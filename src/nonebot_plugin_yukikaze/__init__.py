"""雪风机器人：一个把若干常用功能打包在一起的 NoneBot2 插件。

这里只负责四件事，其余都交给 `plugins/` 下的子插件：

1. 声明插件元数据（``__plugin_meta__``）；
2. 读取统一配置；
3. 按配置把子插件挂上去；
4. 提供 ``雪风帮助`` 命令。

子插件**显式列出**而不是扫描目录：原先的 ``os.listdir`` 会把 ``__pycache__``
一起当成插件名去加载，靠 nonebot 静默失败兜底，而且静态分析工具完全看不见
这份导入关系。现在加一个子插件就是在 `_sub_plugins` 里加一行。

各子插件都基于 OneBot v11 的扩展事件（``PokeNotifyEvent`` /
``GroupBanNoticeEvent`` / 自定义音乐卡片），所以这里如实声明只支持 OneBot v11，
不再从 alconna / uninfo 继承成一幅「跨平台」的样子。
"""

from nonebot import on_command, load_plugin
from nonebot.log import logger
from nonebot.plugin import PluginMetadata, get_plugin_by_module_name

from .config import Config, plugin_config

__plugin_meta__ = PluginMetadata(
    name="雪风机器人",
    description="雪风机器人，带有一些常用的功能，个人项目仅自用",
    usage="发送【雪风帮助】查看当前已启用的功能",
    type="application",
    homepage="https://github.com/hyouryo/nonebot-plugin-yukikaze",
    config=Config,
    supported_adapters={"~onebot.v11"},
    extra={"author": "hyouryo 3433609429@qq.com"},
)


def _sub_plugins(config: Config | None = None) -> dict[str, bool]:
    """子插件名 -> 是否启用。新增子插件时在这里加一行即可。

    ``config`` 只在测试里显式传入；正常调用读全局配置。
    """
    cfg = config if config is not None else plugin_config
    return {
        "poke": cfg.yukikaze_poke_enabled,
        "get_song": cfg.yukikaze_song_enabled,
        "no_talking_laughing": cfg.yukikaze_no_talking_laughing_enabled,
    }


def load_sub_plugins(config: Config | None = None) -> list[str]:
    """按配置加载子插件，返回实际加载成功的名字。"""
    loaded: list[str] = []
    for name, enabled in _sub_plugins(config).items():
        if not enabled:
            logger.debug(f"子插件 {name} 已在配置中关闭，跳过加载")
            continue

        module = f"nonebot_plugin_yukikaze.plugins.{name}"
        if load_plugin(module) is None:
            logger.error(f"子插件 {name} 加载失败，请检查上面的报错")
            continue
        loaded.append(name)
    return loaded


help_cmd = on_command("雪风帮助", aliases={"帮助"}, priority=5)


def _sub_plugin_metadata() -> list[tuple[str, PluginMetadata]]:
    """按固定顺序取出已启用子插件的元数据。

    这里不通过父插件的 ``sub_plugins`` 遍历：只有经过 NoneBot 插件管理器
    （``load_plugin`` / ``load_plugins`` / ``nb plugin``）加载时，父插件才会被
    注册成 Plugin 对象；如果是用户自己 ``import nonebot_plugin_yukikaze``，
    父插件不在注册表里，``sub_plugins`` 也就查不到，而子插件本身仍然可用。
    按模块名查插件在两种情况下都成立。
    """
    result: list[tuple[str, PluginMetadata]] = []
    for name, enabled in _sub_plugins().items():
        if not enabled:
            continue
        plugin = get_plugin_by_module_name(f"nonebot_plugin_yukikaze.plugins.{name}")
        if plugin is None or plugin.metadata is None:
            continue
        result.append((name, plugin.metadata))
    return result


def _help_text() -> str:
    """把已加载子插件的元数据拼成帮助，而不是写死一份必然会过期的文案。"""
    features = _sub_plugin_metadata()
    if not features:
        return "当前没有启用任何功能，请检查 YUKIKAZE_* 配置项"

    lines = [
        f"· {name}：{usage.strip()}" if (usage := meta.usage or "") else f"· {name}"
        for name, meta in features
    ]
    return "雪风帮助\n" + "\n".join(lines)


@help_cmd.handle()
async def _() -> None:
    await help_cmd.finish(_help_text())


load_sub_plugins()
