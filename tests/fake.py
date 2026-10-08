"""构造 onebot v11 假事件的工具。

只保留群消息一种：本插件的三个功能要么是群消息命令，要么在群聊里触发，
私聊事件没有使用方。
"""

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from nonebot.adapters.onebot.v11 import GroupMessageEvent as _GroupMessageEvent


def fake_group_message_event_v11(**field) -> "_GroupMessageEvent":
    import random

    from pydantic import create_model
    from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent
    from nonebot.adapters.onebot.v11.event import Reply, Sender

    _Fake = create_model("_Fake", __base__=GroupMessageEvent)

    class FakeEvent(_Fake):  # type: ignore[misc,valid-type]
        time: int = 1000000
        self_id: int = 1
        post_type: Literal["message"] = "message"
        sub_type: str = "normal"
        user_id: int = 12345678
        message_type: Literal["group"] = "group"
        group_id: int = 87654321
        message_id: int = random.randint(1, 10000000)
        message: Message = Message("test")
        raw_message: str = "test"
        font: int = 0
        sender: Sender = Sender(card="", nickname="test", role="member")
        to_me: bool = False
        reply: Reply | None = None

    return FakeEvent(**field)
