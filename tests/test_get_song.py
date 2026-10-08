"""`get_song` 服务层：这一步在重构前根本没法测。

原实现里 `find_track` / `find_audio` 这些函数会直接调用 `song.finish()`，
必须在真实 matcher 上下文里才跑得动，也就顺带要求打真实网易云接口。
现在它们只依赖一个 `ncm-api-py` 的 Client 接口，喂个假客户端就能覆盖
「搜不到」「无版权」「详情缺字段」这些分支。
"""

from typing import Any

import pytest

from nonebot_plugin_yukikaze.plugins.get_song.service import (
    SearchFailed,
    SongNotFound,
    AudioUnavailable,
    DetailUnavailable,
    build_card,
)


class _FakeResponse:
    """对应 `ncm_api_py.ApiResponse`，只用到 body。"""

    def __init__(self, body: Any) -> None:
        self.body = body
        self.status = 200
        self.cookie: list[str] = []


class _Awaitable:
    """可等待对象；`raises` 非空时在 await 时抛错，模拟接口失败。"""

    def __init__(self, body: Any, raises: type[Exception] | None = None) -> None:
        self._body = body
        self._raises = raises

    def __await__(self):
        async def _run() -> Any:
            if self._raises is not None:
                raise self._raises("接口错误")
            return _FakeResponse(self._body)

        return _run().__await__()


class _FakeClient:
    """每个接口各自返回预设响应；顺便记录 song_url_v1 收到的参数。"""

    def __init__(
        self,
        *,
        search: tuple[Any, type[Exception] | None] = (None, None),
        url: tuple[Any, type[Exception] | None] = (None, None),
        detail: tuple[Any, type[Exception] | None] = (None, None),
    ) -> None:
        self._search, self._search_err = search
        self._url, self._url_err = url
        self._detail, self._detail_err = detail
        self.url_kwargs: dict[str, Any] = {}

    def search(self, keywords: str, **kwargs: Any) -> _Awaitable:
        return _Awaitable(self._search, self._search_err)

    def song_url_v1(self, ids: Any, **kwargs: Any) -> _Awaitable:
        self.url_kwargs = kwargs
        return _Awaitable(self._url, self._url_err)

    def song_detail(self, ids: Any) -> _Awaitable:
        return _Awaitable(self._detail, self._detail_err)


def _search_body(song_id: int = 42, name: str = "晴天") -> dict[str, Any]:
    return {"result": {"songs": [{"id": song_id, "name": name}]}}


def _songs_body(*, name: str = "晴天", pic: str = "http://cover") -> dict[str, Any]:
    return {
        "songs": [
            {
                "name": name,
                "al": {"picUrl": pic},
                "ar": [{"name": "周杰伦"}, {"name": "袁咏琳"}],
            }
        ]
    }


async def test_build_card_happy_path():
    client = _FakeClient(
        search=(_search_body(), None),
        url=({"data": [{"url": "http://audio.mp3"}]}, None),
        detail=(_songs_body(), None),
    )

    card = await build_card("晴天", client=client)  # type: ignore[arg-type]

    assert card.song_id == 42
    assert card.title == "晴天"
    assert card.audio == "http://audio.mp3"
    assert card.cover == "http://cover"
    assert card.artists == "周杰伦/袁咏琳"


async def test_not_found():
    client = _FakeClient(search=({"result": {"songs": []}}, None))
    with pytest.raises(SongNotFound):
        await build_card("不存在的歌", client=client)  # type: ignore[arg-type]


async def test_search_result_missing_result_key():
    """接口返回 200 但结构里没有 result 时也不能崩，应当当成没搜到。"""
    client = _FakeClient(search=({}, None))
    with pytest.raises(SongNotFound):
        await build_card("随便", client=client)  # type: ignore[arg-type]


async def test_audio_is_none_because_of_copyright():
    """url 为 None 是「无版权」的常态，状态码仍是 200。"""
    client = _FakeClient(
        search=(_search_body(), None),
        url=({"data": [{"url": None}]}, None),
    )
    with pytest.raises(AudioUnavailable):
        await build_card("晴天", client=client)  # type: ignore[arg-type]


async def test_audio_data_is_empty():
    client = _FakeClient(
        search=(_search_body(), None),
        url=({"data": []}, None),
    )
    with pytest.raises(AudioUnavailable):
        await build_card("晴天", client=client)  # type: ignore[arg-type]


async def test_detail_missing_fields_fall_back():
    """详情里没有歌名 / 封面 / 歌手时退回搜索结果，不应报错。"""
    client = _FakeClient(
        search=(_search_body(name="七里香"), None),
        url=({"data": [{"url": "http://audio.mp3"}]}, None),
        detail=({"songs": [{}]}, None),
    )

    card = await build_card("七里香", client=client)  # type: ignore[arg-type]

    assert card.title == "七里香"
    assert card.cover == ""
    assert card.artists == ""


async def test_search_error_is_wrapped():
    """`ncm-api-py` 状态码非 200 时抛 RuntimeError，应转成领域异常并带上动作名。"""
    client = _FakeClient(search=(None, RuntimeError))
    with pytest.raises(SearchFailed, match="搜索失败"):
        await build_card("晴天", client=client)  # type: ignore[arg-type]


async def test_detail_error_is_wrapped():
    client = _FakeClient(
        search=(_search_body(), None),
        url=({"data": [{"url": "http://audio.mp3"}]}, None),
        detail=(None, RuntimeError),
    )
    with pytest.raises(DetailUnavailable, match="获取歌曲信息失败"):
        await build_card("晴天", client=client)  # type: ignore[arg-type]


async def test_song_level_config_is_passed_through():
    """`YUKIKAZE_SONG_LEVEL` 必须真的传到 song_url_v1，而不是只写在文档里。"""
    from nonebot_plugin_yukikaze.config import get_config

    config = get_config()
    original = config.yukikaze_song_level
    client = _FakeClient(
        search=(_search_body(), None),
        url=({"data": [{"url": "http://audio.mp3"}]}, None),
        detail=(_songs_body(), None),
    )

    try:
        config.yukikaze_song_level = "lossless"
        await build_card("晴天", client=client)  # type: ignore[arg-type]
    finally:
        config.yukikaze_song_level = original

    assert client.url_kwargs["level"] == "lossless"
