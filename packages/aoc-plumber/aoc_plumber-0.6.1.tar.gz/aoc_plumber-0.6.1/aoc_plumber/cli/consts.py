from datetime import datetime
from pathlib import Path

HOME = Path(__file__).parent.absolute()
NOW = datetime.now()
DAY = NOW.day
MONTH = NOW.month
YEAR = NOW.year if MONTH >= 12 else NOW.year - 1  # Advent of Code runs in December
START_YEAR = 2015
IARG_EMPTY = -1
