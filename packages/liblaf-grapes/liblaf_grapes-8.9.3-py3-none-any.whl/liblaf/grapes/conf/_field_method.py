import functools
from collections.abc import Callable
from typing import Unpack, overload

import attrs
import environs.types

from liblaf.grapes.sentinel import MISSING

from ._constants import METADATA_KEY
from ._entry import Entry
from ._field import Field


@attrs.define
class VarEntry[T](Entry[Field[T]]):
    getter: Callable[[str], T]
    default: T | MISSING = MISSING
    env: str | None = None
    factory: Callable[[], T] | None = None

    def make(self, field: attrs.Attribute, prefix: str) -> Field[T]:
        return Field(
            name=prefix + field.name,
            default=self.default,
            env=self.env,
            factory=self.factory,
            getter=self.getter,
        )


@attrs.define
class FieldMethod[T]:
    wrapped: environs.types.FieldMethod[T]

    @overload
    def __call__(
        self,
        *,
        default: T,
        env: str | None = None,
        **kwargs: Unpack[environs.types.BaseMethodKwargs],
    ) -> Field[T]: ...
    @overload
    def __call__(
        self,
        *,
        default: None,
        env: str | None = None,
        **kwargs: Unpack[environs.types.BaseMethodKwargs],
    ) -> Field[T | None]: ...
    @overload
    def __call__(
        self,
        *,
        factory: Callable[[], T],
        env: str | None = None,
        **kwargs: Unpack[environs.types.BaseMethodKwargs],
    ) -> Field[T]: ...
    @overload
    def __call__(
        self,
        *,
        env: str | None = None,
        factory: None = None,
        **kwargs: Unpack[environs.types.BaseMethodKwargs],
    ) -> Field[T]: ...
    def __call__(
        self,
        *,
        default: T | MISSING | None = MISSING,
        env: str | None = None,
        factory: Callable[[], T] | None = None,
        **kwargs: Unpack[environs.types.BaseMethodKwargs],
    ) -> Field[T] | Field[T | None]:
        return attrs.field(
            metadata={
                METADATA_KEY: VarEntry(
                    getter=functools.partial(self.wrapped, **kwargs),
                    default=default,
                    factory=factory,
                    env=env,
                )
            }
        )


@attrs.define
class ListFieldMethod[T]:
    wrapped: environs.types.ListFieldMethod

    def __call__(
        self,
        subcast: environs.types.Subcast[T] | None = None,
        *,
        delimiter: str | None = None,
        env: str | None = None,
        factory: Callable[[], list[T]] | None = list,
        **kwargs: Unpack[environs.types.BaseMethodKwargs],
    ) -> Field[list[T]]:
        return attrs.field(
            metadata={
                METADATA_KEY: VarEntry(
                    getter=functools.partial(
                        self.wrapped, subcast=subcast, delimiter=delimiter, **kwargs
                    ),
                    factory=factory,
                    env=env,
                )
            }
        )
