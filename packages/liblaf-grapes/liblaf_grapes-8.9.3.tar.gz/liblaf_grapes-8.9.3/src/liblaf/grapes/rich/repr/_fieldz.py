from collections.abc import Generator
from typing import Any

import fieldz
import wrapt
from rich.repr import RichReprResult

from liblaf.grapes.sentinel import MISSING
from liblaf.grapes.typing import is_array
from liblaf.grapes.wadler_lindig import pformat


class ReprWrapper(wrapt.ObjectProxy):
    def __repr__(self) -> str:
        return pformat(self.__wrapped__)


def rich_repr_fieldz(obj: object) -> RichReprResult:
    for name, value, default in _iter_fieldz(obj):
        if default is MISSING:
            yield name, wraps_repr(value)
        else:
            yield name, wraps_repr(value), wraps_repr(default)


def wraps_repr[T](obj: T) -> T:
    if is_array(obj):
        return ReprWrapper(obj)  # pyright: ignore[reportReturnType]
    return obj


def _iter_fieldz(obj: object) -> Generator[tuple[str, Any, Any]]:
    for field in fieldz.fields(obj):
        if not field.repr:
            continue
        value: Any = getattr(obj, field.name, MISSING)
        # rich.repr uses `if default == value:` but does not protect against
        # exceptions. Some types (e.g. NumPy arrays) raise on equality/truth
        # checks (ambiguous truth value). Do the comparison here inside a
        # try/except so we can catch and handle those errors safely.
        try:
            if value == field.default:
                yield field.name, value, field.default
            else:
                yield field.name, value, MISSING
        except Exception:  # noqa: BLE001
            yield field.name, value, MISSING
