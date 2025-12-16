from pathlib import Path
import os
import requests
import re
from glob import glob

from .parse import Iarg, parse_cmd, pat_to_regex, clean_data
from .consts import IARG_EMPTY, MONTH, YEAR, DAY, START_YEAR
from .logger import logger


def download_day(
    day: int,
    year: int,
    cookie: str,
    pattern: str,
    files: tuple[str, ...],
    file_pattern: str,
) -> None:
    folder = Path(pattern.format(day=day, year=year))
    logger.info(f"Downloading data for Day {day} of {year} into folder: {folder}")
    logger.debug(f"Target folder: {folder.absolute()}")
    os.makedirs(folder, exist_ok=True)

    url = f"https://adventofcode.com/{year}/day/{day}"
    response = requests.get(url)
    logger.debug(f"Request to {url} returned status code {response.status_code}")
    if response.status_code == 200:
        data = response.text
        if not (folder / "test.txt").exists():
            try:
                data = clean_data(
                    data.split("<pre><code>", maxsplit=1)[1].split(
                        "</code></pre>", maxsplit=1
                    )[0]
                )
            except IndexError as e:
                logger.warning(
                    f"Failed to extract test data from HTML for Day {day} of {year}: {e}"
                )
            (folder / "test.txt").write_text(
                data
            )
    else:
        logger.warning(
            f"Failed to download test data from {url}. This can happen if the day contains weird test data."
        )

    url += "/input"
    response = requests.get(url, cookies={"session": cookie})
    logger.debug(f"Request to {url} returned status code {response.status_code}")

    if response.status_code == 200:
        if not (folder / "input.txt").exists():
            (folder / "input.txt").write_text(response.text.rstrip())
    else:
        logger.error(
            f"Failed to download data from {url}. This usually means the cookie is invalid."
        )

    for file in filter(None, files):  # Skip empty filenames
        path = folder / file
        if not path.exists():
            logger.debug(f"Creating file: {path}")
            path.write_text(file_pattern)


def main():
    args = parse_cmd()

    if args.write_cookie is not None:
        args.cookie.write_text(args.write_cookie.strip())
        logger.success(f"Wrote new cookie to {args.cookie}")
        exit()

    if not args.cookie.exists():
        logger.error(
            f"Please create a cookie.txt file in the following location ({args.cookie.absolute()})."
            " You can get your session cookie from your browser's developer tools while logged into Advent of Code."
            " Alternatively, you can use the --write-cookie argument with said cookie string to create it."
        )
        exit()

    COOKIE = args.cookie.read_text().strip()

    year: Iarg = args.year if args.year is not None else YEAR
    day: Iarg = args.day if args.day is not None else DAY
    PATTERN: str = args.pattern or ("{year}/Day_{day}" if year != YEAR else "Day_{day}")
    FILES: tuple[str, ...] = tuple(args.files)
    file_pattern: str = args.template
    template_short = file_pattern.replace("\n", "\\n")
    logger.debug(
        f"year={year}, day={day}, pattern={PATTERN}, files={FILES}, template={template_short}"
    )

    # If match, ignore all else
    if args.match is not None:
        glob_pattern = re.sub(r"\{.*\}", "*", args.match)
        compiled_pattern = pat_to_regex(args.match)
        logger.info(
            f"Matching folders with pattern: {args.match} -> {compiled_pattern.pattern}"
        )
        for folder in glob(glob_pattern):
            logger.info(f"Checking folder: {folder}")
            if match := compiled_pattern.match(folder):
                dct = match.groupdict()
                year = int(dct.get("year", YEAR))
                day = int(dct.get("day", DAY))
                download_day(
                    day,
                    year,
                    COOKIE,
                    pattern=folder,
                    files=FILES,
                    file_pattern=file_pattern,
                )
                logger.info(f"Downloaded Day {day} of {year}")
        exit()

    def to_list(
        value: int | tuple[int, int], default: list[int], name: str
    ) -> list[int]:
        if isinstance(value, tuple):
            s, e = value
            if s > e:
                print(f"Invalid {name} range {s}-{e}")
                exit()
            return list(range(s, e + 1))
        return default if value == IARG_EMPTY else [value]

    years = to_list(year, list(range(START_YEAR, YEAR + 1)), "year")
    days = to_list(day, list(range(1, max(26, DAY + 1))), "day")

    for year in years:
        if year < START_YEAR or year > YEAR:
            logger.warning(f"Year {year} is out of valid range ({START_YEAR}-{YEAR})")
            continue
        for day in days:
            if year == YEAR and MONTH == 12 and day > DAY:
                logger.warning(f"Day {day} of this year ({year}) has not arrived yet.")
                break
            download_day(
                day,
                year,
                COOKIE,
                pattern=PATTERN,
                files=FILES,
                file_pattern=file_pattern,
            )
            logger.info(f"Downloaded Day {day} of {year}")
