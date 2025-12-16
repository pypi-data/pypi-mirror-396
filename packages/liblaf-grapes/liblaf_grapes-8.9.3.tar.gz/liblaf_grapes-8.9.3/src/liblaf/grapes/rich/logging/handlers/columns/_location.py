from logging import LogRecord
from typing import override

from rich.text import Text

from ._abc import RichHandlerColumn


class RichHandlerColumnLocation(RichHandlerColumn):
    @override
    def render(self, record: LogRecord) -> Text:
        plain: str = f"{record.name}:{record.funcName}:{record.lineno}"
        return Text(plain, "log.path")
