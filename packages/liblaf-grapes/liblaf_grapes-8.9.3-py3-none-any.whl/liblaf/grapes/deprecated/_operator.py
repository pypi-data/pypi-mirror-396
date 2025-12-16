from __future__ import annotations

from collections.abc import Container, Iterable
from typing import TYPE_CHECKING

from liblaf.grapes.logging import autolog

if TYPE_CHECKING:
    from _typeshed import SupportsContainsAndGetItem


_DEPRECATED_MESSAGE = "'%s' is deprecated. Please use '%s' instead."


def contains[T](
    obj: Container[T],
    key: T,
    deprecated_keys: Iterable[T] = (),
    *,
    msg: str = _DEPRECATED_MESSAGE,
) -> bool:
    if key in obj:
        return True
    for deprecated_key in deprecated_keys:
        if deprecated_key in obj:
            autolog.warning(msg, deprecated_key, key, stacklevel=2)
            return True
    return False


def getitem[KT, VT](
    obj: SupportsContainsAndGetItem[KT, VT],
    key: KT,
    deprecated_keys: Iterable[KT] = (),
    *,
    msg: str = _DEPRECATED_MESSAGE,
) -> VT:
    if key in obj:
        return obj[key]
    for deprecated_key in deprecated_keys:
        if deprecated_key in obj:
            autolog.warning(msg, deprecated_key, key, stacklevel=2)
            return obj[deprecated_key]
    raise KeyError(key)
