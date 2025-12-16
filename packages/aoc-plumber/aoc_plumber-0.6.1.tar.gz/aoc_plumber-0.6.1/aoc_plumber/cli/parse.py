from argparse import ArgumentParser, ArgumentTypeError, Namespace
from pathlib import Path
import html
import re

from .config import load_all_configs
from .utils import Iarg, parse_iarg
from .logger import logger


def valid_iarg(value) -> Iarg:
    res = parse_iarg(value)
    if res is None:
        raise ArgumentTypeError(
            f"Invalid value: {value}. Must be a positive integer,"
            " two dash-separated positive integers, or 'all'."
        )
    return res


def parse_cmd() -> Namespace:
    defaults = load_all_configs()

    parser = ArgumentParser()
    parser.add_argument(
        "-d", "--day", type=valid_iarg, default=defaults.day, help="The day"
    )
    parser.add_argument(
        "-y", "--year", type=valid_iarg, default=defaults.year, help="The year"
    )
    parser.add_argument(
        "-c", "--cookie", type=Path, default=defaults.cookie, help="The cookie file"
    )
    parser.add_argument(
        "-p",
        "--pattern",
        type=str,
        default=defaults.pattern,
        help="The pattern to use for the folder name",
    )
    parser.add_argument(
        "-m",
        "--match",
        type=str,
        default=None,
        help="Match folder structure and fill days that have no data",
    )
    parser.add_argument(
        "--write-cookie",
        type=str,
        default=None,
        help="Write a new cookie string to the cookie file",
    )
    parser.add_argument(
        "-f",
        "--files",
        type=str,
        nargs="+",
        default=defaults.files,
        help="Specify filenames",
    )
    parser.add_argument(
        "-t",
        "--template",
        type=str,
        default=defaults.template,
        help="The template to use for new problem files",
    )

    return parser.parse_args()


def pat_to_regex(pattern) -> re.Pattern:
    escaped_pattern = re.escape(pattern).replace(r"\*", ".*")
    logger.debug(f"Escaped pattern: {pattern} -> {escaped_pattern}")
    named_regex_pattern = re.sub(r"\\\{(\w+).*\\\}", r"(?P<\1>\\d+)", escaped_pattern)
    logger.debug(f"Converted pattern: {pattern} -> {named_regex_pattern}")
    return re.compile(named_regex_pattern)


def clean_data(data: str) -> str:
    return html.unescape(data.removesuffix("\n"))
