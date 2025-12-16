import math
from collections.abc import Iterable

from liblaf.grapes.errors import UnreachableError

# threshold, multiplier, unit
SPECS: list[tuple[int, float, str]] = [
    (-6, 1e9, "ns"),
    (-3, 1e6, "µs"),
    (0, 1e3, "ms"),
    (2, 1, "s"),
]


def duration_magnitude(seconds: float, *, significant: int = 3) -> int:
    number: float = float(f"{seconds:.{significant}e}")
    if number == 0:
        return -10
    seconds = round(seconds)
    if seconds < 100:
        return math.floor(math.log10(abs(number)))
    if seconds < 60 * 60:
        return 2
    if seconds < 24 * 60 * 60:
        return 3
    return 4


def pretty_duration(
    seconds: float, *, magnitude: int | None = None, significant: int = 3
) -> str:
    """.

    Examples:
        >>> pretty_duration(math.nan)
        '?? s'
        >>> pretty_duration(0)
        '.000 ns'
        >>> pretty_duration(1e-13)
        '.000 ns'
        >>> pretty_duration(1e-12)
        '.001 ns'
        >>> pretty_duration(1e-11)
        '.010 ns'
        >>> pretty_duration(1e-10)
        '.100 ns'
        >>> pretty_duration(1e-9)
        '1.00 ns'
        >>> pretty_duration(1e-8)
        '10.0 ns'
        >>> pretty_duration(1e-7)
        '100. ns'
        >>> pretty_duration(1e-6)
        '1.00 µs'
        >>> pretty_duration(1e-5)
        '10.0 µs'
        >>> pretty_duration(1e-4)
        '100. µs'
        >>> pretty_duration(1e-3)
        '1.00 ms'
        >>> pretty_duration(1e-2)
        '10.0 ms'
        >>> pretty_duration(1e-1)
        '100. ms'
        >>> pretty_duration(1.0)
        '1.00 s'
        >>> pretty_duration(1e1)
        '10.0 s'
        >>> pretty_duration(1e2)
        '01:40'
        >>> pretty_duration(1e3)
        '16:40'
        >>> pretty_duration(1e4)
        '02:46:40'
        >>> pretty_duration(1e5)
        '1d,03:46:40'
        >>> pretty_duration(1e6)
        '11d,13:46:40'
    """
    number: str
    unit: str
    number, unit = pretty_duration_unit(
        seconds, magnitude=magnitude, significant=significant
    )
    if unit:
        return f"{number} {unit}"
    return number


def pretty_duration_unit(
    seconds: float, *, magnitude: int | None = None, significant: int = 3
) -> tuple[str, str]:
    if not math.isfinite(seconds):
        return "??", "s"
    if seconds < 0:
        neg: str
        unit: str
        neg, unit = pretty_duration_unit(-seconds, significant=significant)
        return "-" + neg, unit
    if magnitude is None:
        magnitude = duration_magnitude(seconds, significant=significant)
    magnitude = max(min(magnitude, 4), -10)
    for threshold, multiplier, unit in SPECS:
        if magnitude >= threshold:
            continue
        number: float = seconds * multiplier
        precision: int = significant - magnitude - round(math.log10(multiplier)) - 1
        number = round(number, precision)
        width: int = significant + 1
        precision = max(0, precision)
        number_formatted: str = f"{number:#.{precision}f}"
        if width == precision + 1:
            number_formatted = number_formatted.removeprefix("0")
        return number_formatted, unit
    seconds = round(seconds)
    match magnitude:
        case 2:
            minutes: int
            minutes, seconds = divmod(seconds, 60)
            return f"{minutes:02d}:{seconds:02d}", ""
        case 3:
            hours: int
            hours, seconds = divmod(seconds, 3600)
            minutes: int
            minutes, seconds = divmod(seconds, 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}", ""
        case 4:
            days: int
            days, seconds = divmod(seconds, 86400)
            hours: int
            hours, seconds = divmod(seconds, 3600)
            minutes: int
            minutes, seconds = divmod(seconds, 60)
            return f"{days:d}d,{hours:02d}:{minutes:02d}:{seconds:02d}", ""
    raise UnreachableError


def pretty_durations(
    seconds: Iterable[float],
    *,
    magnitude: int | None = None,
    significant: int = 3,
) -> tuple[list[str], str]:
    seconds = list(seconds)
    if magnitude is None:
        magnitude: int = duration_magnitude(max(seconds), significant=significant)
    numbers: list[str] = []
    unit: str = ""
    for val in seconds:
        number: str
        number, unit = pretty_duration_unit(
            val, magnitude=magnitude, significant=significant
        )
        numbers.append(number)
    return numbers, unit
