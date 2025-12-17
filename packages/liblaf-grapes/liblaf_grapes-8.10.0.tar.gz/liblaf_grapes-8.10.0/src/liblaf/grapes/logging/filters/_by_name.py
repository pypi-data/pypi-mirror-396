import logging

import attrs
from typing_extensions import deprecated

from ._utils import as_levelno_dict


@deprecated("Please use `logger.setLevel()` instead.")
@attrs.define
class FilterByName:
    _levels: dict[str, int] = attrs.field(
        converter=as_levelno_dict, factory=lambda: {"__main__": logging.NOTSET}
    )

    def filter(self, record: logging.LogRecord) -> bool:
        level: int | None = self.get_level(record)
        if level is None:
            return True
        return record.levelno >= level

    def get_level(self, record: logging.LogRecord) -> int | None:
        name: str | None = record.name
        while True:
            if not name:
                return None
            level: int | None = self._levels.get(name)
            if level is not None:
                return level
            index: int = name.rfind(".")
            name = None if index < 0 else name[:index]
