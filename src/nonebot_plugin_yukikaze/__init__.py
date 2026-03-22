from nonebot import require
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

import os
from pathlib import Path

import nonebot

plugins = os.listdir(Path(__file__).parent / "plugins")
load_plugins = []
for plugin in plugins:
    load_plugins.append(f"nonebot_plugin_yukikaze.plugins.{plugin}")

sub_plugins = nonebot.load_all_plugins(
    load_plugins,[]
)
from nonebot import on_command

help_cmd = on_command("雪风帮助", aliases={"帮助"}, priority=5)
@help_cmd.handle()
async def _():
    await help_cmd.finish()
