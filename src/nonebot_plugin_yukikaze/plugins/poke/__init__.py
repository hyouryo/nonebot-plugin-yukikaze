import base64
from pathlib import Path
from random import choice

from nonebot import get_plugin_config, on_notice
from nonebot.adapters.onebot.v11 import MessageSegment, PokeNotifyEvent
from nonebot.log import logger
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="poke",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

rule = to_me()

poke_cmd = on_notice(priority=5, rule=rule)


@poke_cmd.handle()
async def _(event: PokeNotifyEvent) -> None:  # noqa: ARG001
    gif = [
        "ok.gif",
        "问号.gif",
        "不愧是我.gif",
        "交给我吧.gif",
        "呃呃.gif",
        "哇~.gif",
        "哼哼.gif",
        "好耶.gif",
        "心碎.gif",
        "生气.gif",
        "脸红.gif",
        "茉子Ciallo.gif",
        "诶？！.gif",
        "可爱.gif",
        "呆.gif",
        "哭哭.gif",
        "啊哈哈.gif",
        "害羞.gif",
        "流汗.gif",
        "笨蛋笨蛋.gif",
        "芳乃Ciallo.gif",
        "蕾娜Ciallo.gif",
        "谢谢.gif",
        "zzz.gif",
        "丛雨Ciallo.gif",
    ]
    src = Path(__file__).parent / "src" / "gif" / choice(gif)
    logger.info(f"{src}")
    with src.open("rb") as src:
        base64_str = base64.b64encode(src.read()).decode()
        base64_str = f"base64://{base64_str}"
        message = MessageSegment.image(base64_str)
        await poke_cmd.send(message, at_sender=True)
