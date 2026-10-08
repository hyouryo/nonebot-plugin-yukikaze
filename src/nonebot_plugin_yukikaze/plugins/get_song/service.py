"""点歌的业务逻辑：搜索 → 取播放链接 → 取歌曲信息。

这层完全不认识 nonebot 的事件响应器，失败时抛 :class:`SongError` 的子类，
由 `__init__.py` 里的 handler 翻译成给用户看的提示。
原实现是在这些函数里直接调 ``song.finish()``，业务逻辑和 matcher 焊死，
既没法单独测试，也没法在别的入口（比如定时任务）复用。

网易云这些接口的「成功」语义很宽松：搜不到歌、歌没有版权或需要会员时，
状态码依然是 200，只是对应数据为空，所以每一步都得自己判空。
"""

from typing import Any
from dataclasses import dataclass

from ncm_api_py import Client, ApiResponse, create_client

from nonebot_plugin_yukikaze.config import plugin_config

#: 卡片上「打开」按钮跳转的网页版地址
SONG_PAGE = "https://music.163.com/#/song?id="


class SongError(Exception):
    """点歌过程中可以直接展示给用户的失败。

    异常自带的文案只描述「哪里失败了」，面向用户的那句话由 handler 组装，
    这样以后想改提示语不用动业务逻辑。
    """


class SearchFailed(SongError):
    """调用搜索接口本身失败，参数是「搜索失败：原因」。"""


class SongNotFound(SongError):
    """搜索成功，但没有命中任何歌曲，参数是关键词。"""


class AudioUnavailable(SongError):
    """歌曲存在，但拿不到播放直链（无版权 / 需要会员），参数是歌名。"""


class DetailUnavailable(SongError):
    """歌曲存在，但取歌曲详情失败，参数是「获取歌曲信息失败：原因」。"""


@dataclass(frozen=True)
class SongCard:
    """自定义音乐卡片所需的全部字段。"""

    song_id: int
    title: str
    audio: str
    cover: str
    artists: str


_client: Client | None = None


def get_client() -> Client:
    """懒加载并复用同一个客户端，避免导入插件时就建连接。

    匿名即可搜索和取链接；想听更高音质或会员歌曲时配置
    ``YUKIKAZE_SONG_COOKIE``。
    """
    global _client
    if _client is None:
        _client = create_client(cookie=plugin_config.yukikaze_song_cookie or None)
    return _client


async def _call(action: str, request: Any, error: type[SongError]) -> ApiResponse:
    """跑一次接口调用，把 ``ncm-api-py`` 的 RuntimeError 转成领域异常。

    异常文案带上动作名（「搜索失败：…」），handler 可以直接透传给用户。
    """
    try:
        return await request
    except RuntimeError as err:
        raise error(f"{action}失败：{err}") from err


def _as_dict(value: Any) -> dict[str, Any]:
    """接口返回的 body 声明成了 Union，这里收窄成 dict。"""
    return value if isinstance(value, dict) else {}


async def find_track(client: Client, keyword: str) -> dict[str, Any]:
    """搜索并返回第一条命中；没有命中是常态，不是异常。"""
    found = await _call("搜索", client.search(keyword, limit=1), SearchFailed)
    tracks = _as_dict(_as_dict(found.body).get("result")).get("songs") or []
    if not isinstance(tracks, list) or not tracks:
        raise SongNotFound(keyword)
    return tracks[0]


async def find_audio(client: Client, song_id: int, name: str) -> str:
    """取播放直链；无版权或需要会员时 ``url`` 为 None，状态码同样是 200。"""
    link = await _call(
        "获取播放链接",
        client.song_url_v1(song_id, level=plugin_config.yukikaze_song_level),
        AudioUnavailable,
    )
    entries = _as_dict(link.body).get("data") or []
    audio = _as_dict(entries[0]).get("url") if entries else None
    if not audio:
        raise AudioUnavailable(name)
    return str(audio)


async def find_card_text(
    client: Client, song_id: int, fallback_name: str
) -> tuple[str, str, str]:
    """取卡片上要显示的歌名 / 封面 / 歌手。

    详情查不到时退回搜索结果的歌名；封面和歌手允许为空，由卡片自己兜底。
    """
    detail = await _call("获取歌曲信息", client.song_detail(song_id), DetailUnavailable)
    songs = _as_dict(detail.body).get("songs") or []
    info = _as_dict(songs[0]) if songs else {}
    title = info.get("name") or fallback_name
    cover = _as_dict(info.get("al")).get("picUrl") or ""
    artists = "/".join(str(artist.get("name", "")) for artist in info.get("ar") or [])
    return str(title), str(cover), artists


async def build_card(keyword: str, client: Client | None = None) -> SongCard:
    """把关键词变成一张音乐卡片；任何一步失败都抛 :class:`SongError`。

    ``client`` 只在测试里显式传入，正常调用走 :func:`get_client`。
    """
    api = client if client is not None else get_client()

    track = await find_track(api, keyword)
    song_id = int(track["id"])
    name = str(track.get("name") or keyword)

    audio = await find_audio(api, song_id, name)
    title, cover, artists = await find_card_text(api, song_id, name)

    return SongCard(
        song_id=song_id,
        title=title,
        audio=audio,
        cover=cover,
        artists=artists,
    )
