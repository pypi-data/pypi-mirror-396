from __future__ import annotations

import attrs

from ._config import BaseConfig
from ._constants import METADATA_KEY
from ._entry import Entry


class GroupEntry[T: BaseConfig](Entry[T]):
    def make(self, field: attrs.Attribute, prefix: str) -> T:
        assert field.type is not None
        return field.type(f"{prefix}{field.name}")


def group[T: BaseConfig]() -> T:  # pyright: ignore[reportInvalidTypeVarUse]
    return attrs.field(metadata={METADATA_KEY: GroupEntry[T]()})
