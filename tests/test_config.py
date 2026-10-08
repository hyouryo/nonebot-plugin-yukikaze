"""配置模型的行为：默认值，以及 `.env` 键名与字段名的对应关系。

NoneBot 的插件配置直接按字段名读环境变量（大小写不敏感），
所以「字段名 == 环境变量名」这条约定一旦被改坏，用户配置就会静默失效。
"""

from nonebot_plugin_yukikaze.config import Config, plugin_config


def test_defaults():
    """未配置时功能全开，音质用 exhigh，cookie 为空（匿名）。"""
    assert plugin_config.yukikaze_poke_enabled is True
    assert plugin_config.yukikaze_song_enabled is True
    assert plugin_config.yukikaze_no_talking_laughing_enabled is True
    assert plugin_config.yukikaze_song_level == "exhigh"
    assert plugin_config.yukikaze_song_cookie == ""
    assert plugin_config.yukikaze_no_talking_laughing_texts == []


def test_texts_accept_json_array():
    """README 里承诺可以用 JSON 数组覆盖播报文案。

    `.env` 里的值都是字符串，只有「来自环境变量」这条路径才会把 JSON 字符串
    解析成列表，所以这里直接驱动 pydantic-settings 的 env source 来验证，
    而不是用 `Config(...)` 传字符串（那条路径不接受字符串）。
    """
    import os

    from pydantic import BaseModel
    from pydantic_settings import EnvSettingsSource

    class _Probe(BaseModel):
        yukikaze_no_talking_laughing_texts: list[str] = []

    os.environ["YUKIKAZE_NO_TALKING_LAUGHING_TEXTS"] = '["甲","乙"]'
    try:
        values = EnvSettingsSource(_Probe, case_sensitive=False)()
    finally:
        del os.environ["YUKIKAZE_NO_TALKING_LAUGHING_TEXTS"]

    assert values["yukikaze_no_talking_laughing_texts"] == ["甲", "乙"]


def test_field_names_are_the_env_var_names():
    """字段名就是 `.env` 里的键名，改名等同于破坏用户配置。"""
    assert set(Config.model_fields) == {
        "yukikaze_poke_enabled",
        "yukikaze_song_enabled",
        "yukikaze_no_talking_laughing_enabled",
        "yukikaze_song_level",
        "yukikaze_song_cookie",
        "yukikaze_no_talking_laughing_texts",
    }
