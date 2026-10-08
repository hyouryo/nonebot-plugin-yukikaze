"""表情包读取与缓存。

只有一个使用方（`poke` 子插件），所以放在它自己的目录里，而不是抽成公共模块。
"""

import base64
from random import choice
from pathlib import Path
from collections import OrderedDict


def _to_base64_uri(path: Path) -> str:
    """把本地图片读成 ``base64://`` 字符串。

    走 base64 而不是本地路径，是为了让图片随消息一起发出去，
    不依赖协议端能访问到机器人所在机器。
    """
    return "base64://" + base64.b64encode(path.read_bytes()).decode()


class ImagePool:
    """一个目录下的图片，按需读取 + base64 编码，并缓存最近用到的若干张。

    表情包是只读资源，编码结果不会变，没必要每次回复都重算（原实现每次戳一戳
    都要读盘 + base64 编码一遍）。但整套表情包接近 3 MB，编码后约 4 MB，
    全量常驻内存也不划算，所以只缓存最近用到的几张。
    """

    def __init__(self, directory: Path, cache_size: int = 8) -> None:
        self._cache_size = cache_size
        self._cache: OrderedDict[Path, str] = OrderedDict()
        # 目录内容在启动时确定，之后不再变化
        self._files: list[Path] = sorted(
            (entry for entry in directory.iterdir() if entry.is_file()),
            key=lambda entry: entry.name,
        )

    def __len__(self) -> int:
        return len(self._files)

    def encode(self, path: Path) -> str:
        """取图片的 base64 URI，命中缓存则直接返回。"""
        if (cached := self._cache.get(path)) is not None:
            self._cache.move_to_end(path)
            return cached

        uri = _to_base64_uri(path)
        self._cache[path] = uri
        self._cache.move_to_end(path)
        while len(self._cache) > self._cache_size:
            self._cache.popitem(last=False)
        return uri

    @property
    def files(self) -> list[Path]:
        return self._files

    def random_uri(self) -> str:
        """随机取一张图片的 URI。目录为空时抛 :class:`LookupError`。"""
        if not self._files:
            raise LookupError("表情包目录下没有任何图片")
        return self.encode(choice(self._files))
