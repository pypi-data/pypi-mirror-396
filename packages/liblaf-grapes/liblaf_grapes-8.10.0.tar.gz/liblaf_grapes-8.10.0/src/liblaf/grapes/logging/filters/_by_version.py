import logging

import attrs
from typing_extensions import deprecated

from liblaf.grapes import magic

from ._utils import as_levelno


@deprecated("Please use `CleanLogger` instead.")
@attrs.define
class FilterByVersion:
    level_dev: int = attrs.field(default=logging.NOTSET, converter=as_levelno)
    level_pre: int = attrs.field(default=logging.DEBUG, converter=as_levelno)

    def filter(self, record: logging.LogRecord) -> bool:
        level: int | None = self.get_level(record)
        if level is None:
            return True
        return record.levelno >= level

    def get_level(self, record: logging.LogRecord) -> int | None:
        file: str = record.pathname
        name: str | None = record.name
        if magic.is_dev_release(file, name):
            return self.level_dev
        if magic.is_pre_release(file, name):
            return self.level_pre
        return None
