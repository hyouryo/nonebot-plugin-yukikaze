"""表情包池：目录扫描、按需编码、缓存上限。"""

import base64
from pathlib import Path

import pytest

from nonebot_plugin_yukikaze.plugins.poke import pool as pool_module
from nonebot_plugin_yukikaze.plugins.poke.pool import ImagePool


def _make_dir(tmp_path: Path, names: list[str]) -> Path:
    directory = tmp_path / "gif"
    directory.mkdir()
    for name in names:
        (directory / name).write_bytes(f"<{name}>".encode())
    return directory


def test_lists_files_in_stable_order(tmp_path: Path):
    directory = _make_dir(tmp_path, ["b.gif", "a.gif", "c.gif"])
    pool = ImagePool(directory)
    assert [path.name for path in pool.files] == ["a.gif", "b.gif", "c.gif"]
    assert len(pool) == 3


def test_encode_returns_base64_uri(tmp_path: Path):
    directory = _make_dir(tmp_path, ["a.gif"])
    pool = ImagePool(directory)
    expected = "base64://" + base64.b64encode(b"<a.gif>").decode()
    assert pool.encode(pool.files[0]) == expected


def test_encode_is_cached(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """同一张图只读一次盘，第二次直接命中缓存。"""
    directory = _make_dir(tmp_path, ["a.gif"])
    pool = ImagePool(directory)

    calls: list[str] = []
    real = pool_module._to_base64_uri

    def counting(path: Path) -> str:
        calls.append(path.name)
        return real(path)

    monkeypatch.setattr(pool_module, "_to_base64_uri", counting)
    target = pool.files[0]
    first = pool.encode(target)
    second = pool.encode(target)

    assert first == second
    assert calls.count("a.gif") == 1, "第二次读取应当命中缓存"


def test_cache_size_is_bounded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """缓存只保留最近用到的 cache_size 张，避免素材全量常驻内存。"""
    directory = _make_dir(tmp_path, ["a.gif", "b.gif", "c.gif"])
    pool = ImagePool(directory, cache_size=2)

    calls: list[str] = []
    real = pool_module._to_base64_uri

    def counting(path: Path) -> str:
        calls.append(path.name)
        return real(path)

    monkeypatch.setattr(pool_module, "_to_base64_uri", counting)

    for path in pool.files:
        pool.encode(path)
    assert len(pool._cache) == 2, "缓存不应超过上限"

    # a.gif 已被淘汰，再次取用时必须重新读盘
    pool.encode(pool.files[0])
    assert calls.count("a.gif") == 2


def test_random_uri_comes_from_the_directory(tmp_path: Path):
    directory = _make_dir(tmp_path, ["a.gif", "b.gif"])
    pool = ImagePool(directory)
    assert pool.random_uri() in {pool.encode(path) for path in pool.files}


def test_empty_directory_raises(tmp_path: Path):
    directory = tmp_path / "empty"
    directory.mkdir()
    pool = ImagePool(directory)
    assert len(pool) == 0
    with pytest.raises(LookupError):
        pool.random_uri()
