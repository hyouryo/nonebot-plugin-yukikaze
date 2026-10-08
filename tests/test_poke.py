"""`poke` 子插件：表情包池，以及戳一戳的事件响应。"""

import pytest
from nonebug import App

from nonebot_plugin_yukikaze.plugins.poke import gifs

FAKE_URI = "base64://ZmFrZQ=="


def test_gif_pool_is_populated_from_bundled_assets():
    """表情包清单来自目录扫描，不再是一份手写列表。"""
    assert len(gifs) >= 20, f"内置表情包似乎变少了：{len(gifs)}"
    assert all(path.suffix == ".gif" for path in gifs.files)


def test_every_gif_encodes_to_base64_uri():
    """逐个编码，确保素材没有损坏、也能被消息段接受。"""
    for path in gifs.files:
        uri = gifs.encode(path)
        assert uri.startswith("base64://")
        assert len(uri) > len("base64://")


@pytest.mark.asyncio
async def test_poke_replies_with_image(
    app: App, monkeypatch: pytest.MonkeyPatch, capture_send
):
    """被戳时回一张图片，并且 @ 对方。"""
    import nonebot
    from nonebot.adapters.onebot.v11 import (
        Bot,
        Adapter,
        MessageSegment,
        PokeNotifyEvent,
    )

    from nonebot_plugin_yukikaze.plugins import poke as module

    monkeypatch.setattr(module.gifs, "encode", lambda path: FAKE_URI)
    event = PokeNotifyEvent(
        time=1000000,
        self_id=1,
        post_type="notice",
        notice_type="notify",
        sub_type="poke",
        user_id=1,
        target_id=1,
        group_id=87654321,
    )

    async with app.test_matcher(module.poke_cmd) as ctx:
        adapter = nonebot.get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        captured = capture_send(bot)
        ctx.receive_event(bot, event)
        ctx.should_finished()

    assert captured.message == MessageSegment.image(FAKE_URI)
    assert captured.kwargs["at_sender"] is True
