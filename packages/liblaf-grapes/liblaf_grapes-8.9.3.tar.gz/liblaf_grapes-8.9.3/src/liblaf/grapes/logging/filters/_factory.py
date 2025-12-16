from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from typing_extensions import deprecated

from ._composite import CompositeFilter

if TYPE_CHECKING:
    from logging import _FilterType

    type FilterLike = _FilterType | Mapping[str, int | str]
else:
    type FilterLike = Any


@deprecated("Please use `CleanLogger()` instead.")
def as_filter(f: FilterLike | None = None, /) -> _FilterType:
    if f is None:
        return CompositeFilter()
    if isinstance(f, Mapping):
        return CompositeFilter(f)
    return f
