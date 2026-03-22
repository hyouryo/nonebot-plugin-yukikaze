from random import choice

from nonebot import on_notice, get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import GroupBanNoticeEvent

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="no_talking_laughing",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

no_talking = on_notice(priority=5)


@no_talking.handle()
async def no_talking_laughing(event: Event) -> None:
    if isinstance(event, GroupBanNoticeEvent):
        talk_texts = (
            "你怎么不说话了，是因为不喜欢吗",
            "你怎么不回我消息，就因为我没发吗",
            "你怎么不说话了，是因为不想说吗",
            "你怎么不发消息了，我还想看你说话呢",
        )
        talk_text = choice(talk_texts)
        await no_talking.finish(talk_text, at_sender=True)
