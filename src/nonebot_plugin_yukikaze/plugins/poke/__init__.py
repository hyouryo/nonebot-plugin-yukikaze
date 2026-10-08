"""戳一戳：回一张随机的表情包。

表情包清单不再逐个写死在 handler 里，而是启动时扫描 ``src/gif`` 目录得到；
编码结果按 LRU 缓存，回复时只做一次字典查找。
"""

from pathlib import Path

from nonebot import on_notice
from nonebot.rule import to_me
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageSegment, PokeNotifyEvent

from .pool import ImagePool

__plugin_meta__ = PluginMetadata(
    name="poke",
    description="被戳一戳时回一张随机表情包",
    usage="戳一戳机器人（需要 @ 或私聊）",
    type="application",
    homepage="https://github.com/hyouryo/nonebot-plugin-yukikaze",
    supported_adapters={"~onebot.v11"},
)

#: 表情包池，只缓存最近用到的 8 张，避免 3 MB 素材全部常驻内存
gifs = ImagePool(Path(__file__).parent / "src" / "gif", cache_size=8)

poke_cmd = on_notice(priority=5, rule=to_me())


@poke_cmd.handle()
async def _(event: PokeNotifyEvent) -> None:
    await poke_cmd.send(MessageSegment.image(gifs.random_uri()), at_sender=True)
