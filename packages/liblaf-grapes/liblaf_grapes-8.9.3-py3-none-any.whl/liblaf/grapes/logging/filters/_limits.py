import functools
import logging
from collections.abc import Iterable
from typing import Any

import attrs
import limits


@attrs.define
class LimitsFilter:
    limiter: limits.strategies.RateLimiter = attrs.field(
        factory=lambda: limits.strategies.FixedWindowRateLimiter(
            limits.storage.MemoryStorage()
        )
    )

    def filter(self, record: logging.LogRecord) -> bool:
        args: Any = getattr(record, "limits", None)
        if args is None:
            return True
        hit_args: _HitArgs = _parse_args(args, record)
        return self.limiter.hit(
            hit_args.item, *hit_args.identifiers, cost=hit_args.cost
        )


@attrs.define
class _HitArgs:
    item: limits.RateLimitItem
    identifiers: Iterable[str]
    cost: int = 1


def _default_identifier(record: logging.LogRecord) -> Iterable[str]:
    return record.pathname, record.funcName, str(record.lineno)


@functools.singledispatch
def _parse_args(args: Any, _record: logging.LogRecord) -> _HitArgs:
    raise ValueError(args)


@_parse_args.register(str)
def _parse_args_str(args: str, record: logging.LogRecord) -> _HitArgs:
    return _HitArgs(item=limits.parse(args), identifiers=_default_identifier(record))


@_parse_args.register(limits.RateLimitItem)
def _parse_args_item(args: limits.RateLimitItem, record: logging.LogRecord) -> _HitArgs:
    return _HitArgs(item=args, identifiers=_default_identifier(record))
