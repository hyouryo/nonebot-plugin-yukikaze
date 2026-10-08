"""点歌：搜索 → 取播放链接 → 取歌曲信息 → 发自定义音乐卡片。

原先依赖本地 3000 端口的 Node 版网易云 API（NeteaseCloudMusicApi），
现在直接用 ncm-api-py（PyO3 绑定 ncm-api-rs），不必再跑外部服务。

业务逻辑都在 `service.py`，这里只负责「把关键词喂进去、把异常翻译成人话」，
所以本文件短到一眼能看完。
"""

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import MessageSegment

from nonebot_plugin_yukikaze.config import Config

from .service import (
    SONG_PAGE,
    SearchFailed,
    SongNotFound,
    AudioUnavailable,
    DetailUnavailable,
    build_card,
)

__plugin_meta__ = PluginMetadata(
    name="get_song",
    description="点歌，发送网易云音乐卡片",
    usage="点歌 <歌曲名>",
    type="application",
    homepage="https://github.com/hyouryo/nonebot-plugin-yukikaze",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

song = on_command("点歌")


@song.handle()
async def _(message: Message = CommandArg()):
    keyword = message.extract_plain_text().strip()
    if not keyword:
        await song.finish("请输入歌曲名，例如：点歌 晴天")

    try:
        card = await build_card(keyword)
    except SongNotFound:
        await song.finish(f"没有搜到「{keyword}」")
    except AudioUnavailable as err:
        await song.finish(f"《{err}》没有可用的播放链接（可能无版权或需要会员）")
    except (SearchFailed, DetailUnavailable) as err:
        await song.finish(str(err))

    await song.send(
        MessageSegment.music_custom(
            url=f"{SONG_PAGE}{card.song_id}",
            audio=card.audio,
            title=card.title,
            img_url=card.cover,
            content=card.artists,
        )
    )
