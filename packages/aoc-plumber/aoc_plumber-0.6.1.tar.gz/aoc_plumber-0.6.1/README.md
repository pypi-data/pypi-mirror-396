# AOC Tooling made simple(ish)

### Logging
Override with env var `AOCP_LOG_LEVEL` (e.g., `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). Default is `INFO`.

### Per-project defaults
Create a `.aocplumber.toml` (or `aocplumber.toml`) in your working directory to override CLI defaults without typing them each run. Example:

```toml
pattern = "day_{day:02d}"
files = ["main.py"]
day = "1-5"
year = 2024
cookie = "./cookie.txt"
```

Keys you can set: `day`, `year` (`int`, `"all"`, or `"{start:d}-{end:d}"`), `pattern` (folder format string), `files` (string or list), `template` (string for new files), and `cookie` (path). CLI flags still override these defaults.