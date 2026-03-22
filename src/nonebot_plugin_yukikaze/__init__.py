from nonebot import logger, require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_uninfo")
require("nonebot_plugin_alconna")
require("nonebot_plugin_localstore")
require("nonebot_plugin_apscheduler")
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="雪风机器人",
    description="雪风机器人，带有一些常用的功能，个人项目仅自用",
    usage="发送【雪风帮助】以获取帮助",
    type="application",  # library
    homepage="https://github.com/hyouryo/nonebot-plugin-yukikaze",
    config=Config,
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_uninfo"
    ),
    # supported_adapters={"~onebot.v11"}, # 仅 onebot
    extra={"author": "hyouryo 3433609429@qq.com"},
)

from arclet.alconna import Args, Option, Alconna, Arparma, Subcommand
from nonebot_plugin_alconna import on_alconna
from nonebot_plugin_alconna.uniseg import UniMessage

pip = on_alconna(
    Alconna(
        "pip",
        Subcommand(
            "install",
            Args["package", str],
            Option("-r|--requirement", Args["file", str]),
            Option("-i|--index-url", Args["url", str]),
        ),
    )
)


@pip.handle()
async def _(result: Arparma):
    package: str = result.other_args["package"]
    logger.info(f"installing {package}")
    await UniMessage.text(package).send()
    
import nonebot
from pathlib import Path

sub_plugins = nonebot.load_plugins(
    str(Path(__file__).parent.joinpath("plugins").resolve())
)

a = nonebot.on_command("test")
@a.handle()
async def _():
    plugins = ""
    for i in sub_plugins:
        plugins += f"{i}\n"
    await a.send(plugins)