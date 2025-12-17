import logging
import types
from typing import Any

from liblaf.grapes import magic

_PROXY_METHODS: set[str] = {
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "log",
    "exception",
    "findCaller",
}


class AutoLogger:
    def __getattr__(self, name: str) -> Any:
        if name in _PROXY_METHODS:

            def wrapper(*args, **kwargs) -> None:
                depth: int = kwargs.get("stacklevel", 1)
                frame: types.FrameType | None
                stacklevel: int
                frame, stacklevel = magic.get_frame_with_stacklevel(
                    depth=depth + 1, hidden=magic.hidden_from_logging
                )
                logger_name: str | None = None
                if frame is not None:
                    logger_name = frame.f_globals.get("__name__")
                logger: logging.Logger = logging.getLogger(logger_name)
                kwargs["stacklevel"] = stacklevel
                return getattr(logger, name)(*args, **kwargs)

            return wrapper

        frame: types.FrameType | None = magic.get_frame(depth=2)
        logger_name: str | None = None
        if frame is not None:
            logger_name = frame.f_globals.get("__name__")
        logger: logging.Logger = logging.getLogger(logger_name)
        return getattr(logger, name)


autolog = AutoLogger()
