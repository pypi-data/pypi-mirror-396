from collections.abc import Callable, Generator, Iterable
from typing import Any

import attrs
import wrapt


@attrs.define
class CacheIter[T]:
    _iter: Iterable[T]
    _cache: list[T] = attrs.field(repr=False, init=False, factory=list)

    def __iter__(self) -> Generator[T]:
        yield from self._cache
        for item in self._iter:
            self._cache.append(item)
            yield item


def cache_iter[C: Callable[..., Iterable]](func: C) -> C:
    @wrapt.decorator
    def wrapper[T](
        wrapped: Callable[..., Iterable[T]],
        _instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Iterable[T]:
        return CacheIter(wrapped(*args, **kwargs))

    return wrapper(func)  # pyright: ignore[reportReturnType]
