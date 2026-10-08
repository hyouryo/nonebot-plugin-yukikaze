"""有人在群里被禁言时，机器人替他「说句话」。

原先的 handler 接收的是通用 :class:`Event`，靠 ``isinstance`` 判断类型，
等于对所有通知事件都跑一遍；这里直接把事件类型收窄成 ``GroupBanNoticeEvent``，
不匹配的事件根本不会进来。
"""

from random import choice

from nonebot import on_notice
from nonebot.rule import to_me
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import GroupBanNoticeEvent

from nonebot_plugin_yukikaze.config import Config, plugin_config

__plugin_meta__ = PluginMetadata(
    name="no_talking_laughing",
    description="群成员被禁言时随机说一句风凉话",
    usage="被动触发：有人被禁言时自动播报",
    type="application",
    homepage="https://github.com/hyouryo/nonebot-plugin-yukikaze",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

#: 默认文案，可用 YUKIKAZE_NO_TALKING_LAUGHING_TEXTS 覆盖
DEFAULT_TEXTS: tuple[str, ...] = (
    "你怎么不说话了，是因为不喜欢吗",
    "你怎么不回我消息，就因为我没发吗",
    "你怎么不说话了，是因为不想说吗",
    "你怎么不发消息了，我还想看你说话呢",
)

no_talking = on_notice(priority=5, rule=to_me())


@no_talking.handle()
async def _(event: GroupBanNoticeEvent) -> None:
    texts = plugin_config.yukikaze_no_talking_laughing_texts or list(DEFAULT_TEXTS)
    await no_talking.finish(choice(texts), at_sender=True)
