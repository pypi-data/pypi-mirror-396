from collections.abc import Iterable
from typing import Any, TypeAlias
from aoc_plumber.cli.consts import IARG_EMPTY

Iarg: TypeAlias = int | tuple[int, int]


def parse_iarg(value: str) -> Iarg | None:
    if value.isdigit():
        return int(value)
    if value == "all":
        return IARG_EMPTY
    if (
        "-" in value
        and len(parts := value.split("-")) == 2
        and all(map(str.isdigit, parts))
    ):
        return tuple(map(int, parts))  # type: ignore
    return None


def normalize_iarg(value: Any) -> Iarg | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return parse_iarg(value)
    if isinstance(value, Iterable) and not isinstance(value, str):
        collected = list(value)
        if len(collected) == 2 and all(isinstance(x, int) for x in collected):
            return tuple(collected)  # type: ignore[return-value]
    return None
