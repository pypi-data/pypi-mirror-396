from pathlib import Path
import tomli
from typing import Any, Iterable, overload, Literal

from .logger import logger
from .consts import HOME
from .models import ConfigModel

SUPP_CONFIGS: tuple[Path | str, ...] = (
    ".aocplumber.toml",
    "../.aocplumber.toml",
)


@overload
def load_config(path: Path, err_fatal: Literal[True]) -> dict[str, Any]: ...


@overload
def load_config(path: Path) -> dict[str, Any] | None: ...


def load_config(path: Path, err_fatal: bool = False) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = tomli.loads(path.read_text())
        logger.debug(f"Loaded config from {path}")
        return data
    except Exception as e:
        if err_fatal:
            logger.error(
                f"Default library config file {path} is not valid TOML; aborting"
            )
            raise e
        logger.warning(f"Failed to read {path}: {e}")
    return None


def eval_locations(locations: Iterable[Path | str]) -> Iterable[Path]:
    return [
        Path.cwd() / location if isinstance(location, str) else location
        for location in locations
    ]


def load_all_configs() -> ConfigModel:
    """Load and merge all config files in order (library defaults first, then project configs).

    Later configs override earlier ones. Returns a validated ConfigModel.
    """
    merged_dict: dict[str, Any] = (
        load_config(HOME / ".aocplumber.toml", err_fatal=True) or {}
    )
    logger.debug(f"Initial config: {merged_dict}")
    for path in eval_locations(SUPP_CONFIGS):
        config_dict = load_config(path)
        if config_dict:
            merged_dict.update(config_dict)
            logger.debug(f"Merged config: {merged_dict}")
    return ConfigModel(**merged_dict)
