from __future__ import annotations

from collections.abc import Container, Iterable
from typing import TYPE_CHECKING

from liblaf.grapes import magic
from liblaf.grapes.logging import autolog

if TYPE_CHECKING:
    from _typeshed import SupportsGetItem


_DEPRECATED_MESSAGE = "'%s' is deprecated. Please use '%s' instead."


def contains[T](
    obj: Container[T],
    key: T,
    deprecated_keys: Iterable[T] = (),
    *,
    msg: str = _DEPRECATED_MESSAGE,
) -> bool:
    __warnings_hide = True
    if key in obj:
        return True
    for deprecated_key in deprecated_keys:
        if deprecated_key in obj:
            stacklevel: int
            _, stacklevel = magic.get_frame_with_stacklevel(
                hidden=magic.hidden_from_warnings
            )
            autolog.warning(msg, deprecated_key, key, stacklevel=stacklevel)
            return True
    return False


def getitem[KT, VT](
    obj: SupportsGetItem[KT, VT],
    key: KT,
    deprecated_keys: Iterable[KT] = (),
    *,
    msg: str = _DEPRECATED_MESSAGE,
) -> VT:
    __warnings_hide = True
    try:
        return obj[key]
    except KeyError:
        pass
    for deprecated_key in deprecated_keys:
        try:
            value: VT = obj[deprecated_key]
        except KeyError:
            continue
        stacklevel: int
        _, stacklevel = magic.get_frame_with_stacklevel(
            hidden=magic.hidden_from_warnings
        )
        autolog.warning(msg, deprecated_key, key, stacklevel=stacklevel)
        return value
    raise KeyError(key)
