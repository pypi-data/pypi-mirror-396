import functools
from collections.abc import Callable
from typing import Any


def wraps[C: Callable](wrapped: C) -> Callable[[Any], C]:
    def decorator(wrapper: Any) -> C:
        wrapper = functools.update_wrapper(wrapper, wrapped)
        return wrapper

    return decorator
