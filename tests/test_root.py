"""根插件：`.`env` 开关决定加载哪些子插件。

这里只覆盖「开关 → 待加载列表」这段纯逻辑；真正 load_plugin 的行为由
子插件各自的测试和本文件末尾的注册断言覆盖。
"""

from nonebot_plugin_yukikaze import _sub_plugins
from nonebot_plugin_yukikaze.config import Config


def test_all_enabled_by_default():
    assert _sub_plugins(Config()) == {
        "poke": True,
        "get_song": True,
        "no_talking_laughing": True,
    }


def test_individual_switches():
    assert _sub_plugins(Config(yukikaze_poke_enabled=False)) == {
        "poke": False,
        "get_song": True,
        "no_talking_laughing": True,
    }
    assert _sub_plugins(Config(yukikaze_song_enabled=False))["get_song"] is False
    assert (
        _sub_plugins(Config(yukikaze_no_talking_laughing_enabled=False))[
            "no_talking_laughing"
        ]
        is False
    )


def test_all_disabled():
    """全关时没有任何子插件待加载，帮助文案也要给出可读的提示。"""
    config = Config(
        yukikaze_poke_enabled=False,
        yukikaze_song_enabled=False,
        yukikaze_no_talking_laughing_enabled=False,
    )
    assert not any(_sub_plugins(config).values())


def test_loaded_sub_plugins_are_nested():
    """默认配置下三个子插件都应挂成父插件的子插件（不是散装模块）。"""
    from nonebot.plugin import get_plugin

    parent = get_plugin("nonebot_plugin_yukikaze")
    assert parent is not None
    assert {sub.name for sub in parent.sub_plugins} == {
        "poke",
        "get_song",
        "no_talking_laughing",
    }
    assert all(sub.parent_plugin is parent for sub in parent.sub_plugins)
