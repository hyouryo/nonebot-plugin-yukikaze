"""`no_talking_laughing` 子插件：禁言播报。

事件类型已经收窄成 `GroupBanNoticeEvent`，所以这里重点验证
「只有机器人自己被禁言才播报」这条规则。文案是随机挑的，测试里把
``choice`` 固定住，断言才是确定性的。
"""

import pytest
from nonebug import App

from nonebot_plugin_yukikaze.plugins.no_talking_laughing import (
    DEFAULT_TEXTS,
    no_talking,
)


def _ban_event(*, user_id: int = 1, self_id: int = 1):
    from nonebot.adapters.onebot.v11 import GroupBanNoticeEvent

    return GroupBanNoticeEvent(
        time=1000000,
        self_id=self_id,
        post_type="notice",
        notice_type="group_ban",
        sub_type="ban",
        user_id=user_id,
        group_id=87654321,
        operator_id=2,
        duration=600,
    )


@pytest.mark.asyncio
async def test_ban_notice_triggers_reply(
    app: App, monkeypatch: pytest.MonkeyPatch, capture_send
):
    """机器人自己被禁言时，@ 上当事人并说一句文案。"""
    import nonebot
    from nonebot.adapters.onebot.v11 import Bot, Adapter

    # 文案是随机挑的，把子插件里的 choice 固定住，断言才是确定性的。
    # 必须打在子插件模块上：它是 `from random import choice` 之后直接调用的。
    monkeypatch.setattr(
        "nonebot_plugin_yukikaze.plugins.no_talking_laughing.choice",
        lambda seq: seq[0],
    )
    event = _ban_event()

    async with app.test_matcher(no_talking) as ctx:
        adapter = nonebot.get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        captured = capture_send(bot)
        ctx.receive_event(bot, event)
        ctx.should_finished()

    # 捕获到的是 handler 传入的原始字符串，比较文本即可
    assert str(captured.message) == DEFAULT_TEXTS[0]
    assert captured.kwargs["at_sender"] is True


@pytest.mark.asyncio
async def test_ban_of_other_member_is_ignored(app: App):
    """别人被禁言时不插嘴：规则是 to_me()，只有机器人自己中招才播报。"""
    import nonebot
    from nonebot.adapters.onebot.v11 import Bot, Adapter

    event = _ban_event(user_id=999, self_id=1)

    async with app.test_matcher(no_talking) as ctx:
        adapter = nonebot.get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        ctx.receive_event(bot, event)
        ctx.should_not_pass_rule()


def test_default_texts_available():
    assert len(DEFAULT_TEXTS) == 4
    assert all(isinstance(text, str) and text for text in DEFAULT_TEXTS)
