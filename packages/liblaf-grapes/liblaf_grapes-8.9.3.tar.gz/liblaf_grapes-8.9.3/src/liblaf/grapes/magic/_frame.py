import inspect
import types
from collections.abc import Callable

from liblaf.grapes._config import config

from ._release_type import is_pre_release

_HIDDEN_FROM_LOGGING_NAMES: tuple[str, ...] = ("rich.progress.",)


def hidden_from_logging(frame: types.FrameType | None) -> bool:
    if frame is None:
        return True
    if frame.f_locals.get("__tracebackhide__", False):
        return True
    name: str = frame.f_globals.get("__name__", "")
    return f"{name}.".startswith(_HIDDEN_FROM_LOGGING_NAMES)


def hidden_from_traceback(
    frame: types.FrameType | None, *, hide_stable_release: bool | None = None
) -> bool:
    if frame is None:
        return True
    if frame.f_locals.get("__tracebackhide__", False):
        return True
    if hide_stable_release is None:
        hide_stable_release = config.traceback.hide_stable_release.get()
    if hide_stable_release:
        name: str | None = frame.f_globals.get("__name__")
        if not is_pre_release(frame.f_code.co_filename, name):
            return True
    return False


def get_frame(
    depth: int = 1, hidden: Callable[[types.FrameType], bool] | None = None
) -> types.FrameType | None:
    frame: types.FrameType | None = inspect.currentframe()
    while frame is not None and depth > 0:
        frame = frame.f_back
        depth -= 1
        if hidden is not None:
            while frame is not None and hidden(frame):
                frame = frame.f_back
    return frame


def get_frame_with_stacklevel(
    depth: int = 1, hidden: Callable[[types.FrameType], bool] | None = None
) -> tuple[types.FrameType | None, int]:
    frame: types.FrameType | None = inspect.currentframe()
    stacklevel: int = 0
    while frame is not None and depth > 0:
        frame = frame.f_back
        depth -= 1
        stacklevel += 1
        if hidden is not None:
            while frame is not None and hidden(frame):
                frame = frame.f_back
                stacklevel += 1
    return frame, stacklevel
