import functools
from typing import Any

import attrs

from liblaf.grapes.functools import wraps
from liblaf.grapes.rich.repr import rich_repr_fieldz
from liblaf.grapes.wadler_lindig import pdoc_fieldz, pdoc_rich_repr, pformat


@wraps(attrs.define)
def define(maybe_cls: type | None = None, **kwargs) -> Any:
    if maybe_cls is None:
        return functools.partial(define, **kwargs)
    cls: type = maybe_cls
    auto_detect: bool = kwargs.get("auto_detect", True)
    repr_: bool | None = kwargs.get("repr")
    if auto_detect and repr_ is None and cls.__repr__ is object.__repr__:
        repr_ = True
    if repr_:
        cls.__repr__ = pformat  # pyright: ignore[reportAttributeAccessIssue]
        kwargs["repr"] = False
    if not hasattr(cls, "__pdoc__"):
        if hasattr(cls, "__rich_repr__"):
            cls.__pdoc__ = pdoc_rich_repr
        else:
            cls.__pdoc__ = pdoc_fieldz
    if not hasattr(cls, "__rich_repr__"):
        cls.__rich_repr__ = rich_repr_fieldz
    return attrs.define(cls, **kwargs)
