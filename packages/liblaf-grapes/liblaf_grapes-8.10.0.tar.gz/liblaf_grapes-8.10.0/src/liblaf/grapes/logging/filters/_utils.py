import logging
from collections.abc import Mapping

import tlz


def as_levelno_dict(levels: Mapping[str, int | str]) -> dict[str, int]:
    level_names_mapping: dict[str, int] = logging.getLevelNamesMapping()
    return tlz.valmap(
        lambda level: level if isinstance(level, int) else level_names_mapping[level],
        levels,
    )


def as_levelno(level: int | str) -> int:
    if isinstance(level, int):
        return level
    level_names_mapping: dict[str, int] = logging.getLevelNamesMapping()
    return level_names_mapping[level]
