import logging
from collections.abc import Mapping

import attrs
import cachetools
from typing_extensions import deprecated

from ._by_name import FilterByName
from ._by_version import FilterByVersion
from ._once import FilterOnce
from ._utils import as_levelno


@deprecated("Please use `CleanLogger` instead.")
@attrs.define
class CompositeFilter:
    by_name: FilterByName = attrs.field(factory=FilterByName)
    by_version: FilterByVersion = attrs.field(factory=FilterByVersion)
    level: int = attrs.field(default=logging.WARNING)
    once: FilterOnce = attrs.field(factory=FilterOnce)

    _cache: cachetools.LRUCache[str, int] = attrs.field(
        repr=False, init=False, factory=lambda: cachetools.LRUCache(maxsize=1024)
    )

    def __init__(self, by_name: Mapping[str, int | str] | None = None) -> None:
        if by_name is None:
            by_name = {"__main__": logging.NOTSET}
        level: int = as_levelno(by_name.get("", logging.WARNING))
        self.__attrs_init__(by_name=FilterByName(by_name), level=level)  # pyright: ignore[reportAttributeAccessIssue]

    def filter(self, record: logging.LogRecord) -> bool:
        if not self.once(record):
            return False
        level: int = self.get_level(record)
        return record.levelno >= level

    def get_level(self, record: logging.LogRecord) -> int:
        cached: int = self._cache.get(record.name, -1)
        if cached == -1:
            level: int | None = self._get_level_uncached(record)
            if level is None:
                level = self.level
            self._cache[record.name] = cached = level
        return cached

    def _get_level_uncached(self, record: logging.LogRecord) -> int | None:
        level: int | None = self.by_name.get_level(record)
        if level is not None:
            return level
        level = self.by_version.get_level(record)
        if level is not None:
            return level
        return None
