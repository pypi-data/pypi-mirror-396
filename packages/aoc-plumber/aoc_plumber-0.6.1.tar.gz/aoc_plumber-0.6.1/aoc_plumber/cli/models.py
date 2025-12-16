from pathlib import Path
from typing import Any, Iterable
from pydantic import BaseModel, field_validator

from aoc_plumber.cli.consts import HOME

from .utils import Iarg, normalize_iarg


class ConfigModel(BaseModel):
    day: Iarg | None = None
    year: Iarg | None = None
    cookie: Path | None = None
    pattern: str | None = None
    files: tuple[str, ...] | None = None
    template: str | None = None

    @field_validator("day", "year", mode="before")
    @classmethod
    def validate_iarg(cls, v: Any) -> Iarg | None:
        return normalize_iarg(v)

    @field_validator("files", mode="before")
    @classmethod
    def validate_files(cls, v: Any) -> tuple[str, ...] | None:
        if v is None:
            return None
        if isinstance(v, str):
            return (v,)
        if isinstance(v, Iterable):
            return tuple(str(v) for v in v if v)
        return None

    @field_validator("cookie", mode="before")
    @classmethod
    def validate_cookie(cls, v: Any) -> Path | None:
        if v is None:
            return None
        if isinstance(v, Path):
            return v
        if isinstance(v, str):
            # Support {CLI}/path expansion
            if v.startswith("{CLI}/"):
                return HOME / v[6:]
            return Path(v)
        return None
