"""插件配置。

NoneBot 的插件配置直接读环境变量：**字段名就是 `.env` 里的键名**（大小写不敏感），
所以这里的字段刻意带上 ``yukikaze_`` 前缀，避免和别的插件撞车。

配置用 :data:`plugin_config` 惰性读取：在 import 期就调 ``get_plugin_config``
会要求 NoneBot 已经初始化，那样这几个模块就没法单独 import（测试会被迫
先起一个完整的 NoneBot），所以推迟到第一次真正取配置时再解析。
"""

from typing import Any
from functools import lru_cache

from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    """雪风机器人的全部配置项，对应 `.env` 中同名（大写）的环境变量。"""

    # —— 功能开关 ——
    #: 戳一戳回复表情包
    yukikaze_poke_enabled: bool = True
    #: 点歌
    yukikaze_song_enabled: bool = True
    #: 全员禁言时的播报
    yukikaze_no_talking_laughing_enabled: bool = True

    # —— 点歌 ——
    #: 音质，可选 standard/higher/exhigh/lossless/hires/sky
    yukikaze_song_level: str = "exhigh"
    #: 网易云 cookie（``MUSIC_U=...``）。留空则匿名，只能取到无需会员的歌曲
    yukikaze_song_cookie: str = ""

    # —— 禁言播报 ——
    #: 随机挑选的文案。留空则使用内置默认文案
    yukikaze_no_talking_laughing_texts: list[str] = []


@lru_cache(maxsize=1)
def get_config() -> Config:
    """读取一次配置并缓存；每个进程内只解析一次。"""
    return get_plugin_config(Config)


class _LazyConfig:
    """把 :func:`get_config` 包装成「看起来就是 Config 实例」的代理。

    多个子插件会在自己的 import 期读配置，如果那时就调用 ``get_config()``，
    等于把「NoneBot 必须已初始化」这个前提扩散到所有子插件；用代理则只在
    真正访问具体字段时才解析。
    """

    __slots__ = ()

    def __getattr__(self, name: str) -> Any:
        return getattr(get_config(), name)


plugin_config: Config = _LazyConfig()  # type: ignore[assignment]
