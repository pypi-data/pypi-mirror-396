from pathlib import Path

from liblaf.grapes import conf
from liblaf.grapes.conf import BaseConfig, Field


class ConfigLogging(BaseConfig):
    datefmt: Field[str] = conf.str(default="YYYY-MM-DD HH:mm:ss.SSS", env="LOG_DATEFMT")
    file: Field[Path | None] = conf.path(default=None, env="LOG_FILE")
    hide_frame: Field[list[str]] = conf.list(factory=lambda: ["rich.progress"])
    level: Field[str] = conf.str(default="TRACE")
    time_relative: Field[bool] = conf.bool(default=True, env="LOG_TIME_RELATIVE")
