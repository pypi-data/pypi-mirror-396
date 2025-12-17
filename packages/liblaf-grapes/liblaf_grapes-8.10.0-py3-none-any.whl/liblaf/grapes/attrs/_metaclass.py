from typing import Any, dataclass_transform

import attrs

from ._define import define


@dataclass_transform(field_specifiers=(attrs.field,))
class AttrsMeta(type):
    def __new__[T: type](
        mcs: type[T],
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        /,
        **kwargs: Any,
    ) -> T:
        cls: T = super().__new__(mcs, name, bases, namespace)
        if "__attrs_attrs__" in namespace:
            return cls
        cls = define(cls, **kwargs)
        return cls


@dataclass_transform(field_specifiers=(attrs.field,))
class Attrs(metaclass=AttrsMeta): ...
