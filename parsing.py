import sys
from typing import TypedDict

MANDATORY_KEYS = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}


class ConfigError(Exception):
    pass


class Config(TypedDict):
    WIDTH: int
    HEIGHT: int
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str
    PERFECT: bool


def parse_config(path: str) -> Config:
    """Parse and validate a maze config file into a settings dict.

    Reads simple `KEY = value` lines (blank lines and lines starting with
    '#' are skipped), uppercases keys, and checks that all mandatory keys
    are present. WIDTH and HEIGHT are converted to positive ints, ENTRY
    and EXIT to (x, y) coordinate tuples validated against those bounds,
    and PERFECT to a bool. Entry and exit must differ, and OUTPUT_FILE
    must be non-empty.

    Args:
        path: Path to the config file to read.

    Returns:
        A dict with keys WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT
        (plus any other keys found in the file), with values converted
        to their proper types.

    Raises:
        ConfigError: If the file can't be read, a line is malformed,
            a mandatory key is missing, or any value fails validation.
    """
    raw: dict[str, str] = {}

    try:
        with open(path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}")
    except OSError as e:
        raise ConfigError(f"Could not read config file: {e}")

    # parsing lines (value will overwrite if repeat assignment)
    # (line can only have 1 "="")
    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if line.count("=") != 1:
            raise ConfigError(f"Line {lineno}: \
                              expected one '=', got: {line!r}")

        key, value = line.split("=", 1)
        key = key.strip().upper()
        value = value.strip()

        if not key:
            raise ConfigError(f"Line {lineno}: empty key")
        if not value:
            raise ConfigError(f"Line {lineno}: empty value for key {key}")

        raw[key] = value

    # dict validation, parse_coord always called
    # AFTER validating widthe and height!
    missing = MANDATORY_KEYS - raw.keys()
    if missing:
        raise ConfigError(f"Missing mandatory key(s): \
                          {", ".join(sorted(missing))}")

    width = parse_positive_int(raw["WIDTH"], "WIDTH")
    height = parse_positive_int(raw["HEIGHT"], "HEIGHT")

    config: Config = {
        "WIDTH": width,
        "HEIGHT": height,
        "ENTRY": parse_coord(raw["ENTRY"], "ENTRY", width, height),
        "EXIT": parse_coord(raw["EXIT"], "EXIT", width, height),
        "OUTPUT_FILE": raw["OUTPUT_FILE"],
        "PERFECT": parse_bool(raw["PERFECT"], "PERFECT"),
    }

    if config["ENTRY"] == config["EXIT"]:
        raise ConfigError("Entry and exit cannot be the same")

    if not config["OUTPUT_FILE"]:
        raise ConfigError("OUTPUT_FILE cannot be empty")

    return config


def parse_positive_int(value: str, key: str) -> int:
    """Parse a string as a strictly positive integer.

    Args:
        value: The raw string value to parse.
        key: Name of the config key this value belongs to, used only
            for error messages.

    Returns:
        The parsed integer.

    Raises:
        ConfigError: If value is not a valid integer, or is <= 0.
    """
    try:
        n = int(value)
    except ValueError:
        raise ConfigError(f"{key} must be an integer, got: {value!r}")
    if n <= 0:
        raise ConfigError(f"{key} must be a positive integer, got: {n}")
    return n


def parse_coord(value: str, key: str,
                width: int, height: int) -> tuple[int, int]:
    """Parse a string as an "x,y" coordinate within maze bounds.

    Args:
        value: The raw string value to parse, expected as "x,y".
        key: Name of the config key this value belongs to, used only
            for error messages.
        width: Maze width; the parsed x must not exceed this.
        height: Maze height; the parsed y must not exceed this.

    Returns:
        The parsed (x, y) coordinate as a tuple of ints.

    Raises:
        ConfigError: If value isn't formatted as two comma-separated
            integers, either coordinate is negative, or a coordinate
            exceeds the given width/height.
    """
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(f"{key} must be formatted as x,y, got: {value!r}")
    try:
        x, y = int(parts[0].strip()), int(parts[1].strip())
    except ValueError:
        raise ConfigError(f"{key} coordinates must be integers, \
                          got: {value!r}")
    if x < 0 or y < 0:
        raise ConfigError(f"{key} coordinates must be non-negative, \
                          got: {value!r}")

    # validate coordinates are within bounds
    if x > width or y > height:
        raise ConfigError(
            f"{key} coordinates are out of maze bounds "
            f"(width)={width}, height={height}"
        )

    return (x, y)


def parse_bool(value: str, key: str) -> bool:
    """Parse a string as a boolean.

    Accepts "true"/"1"/"yes" as True and "false"/"0"/"no" as False,
    case-insensitive.

    Args:
        value: The raw string value to parse.
        key: Name of the config key this value belongs to, used only
            for error messages.

    Returns:
        The parsed boolean.

    Raises:
        ConfigError: If value doesn't match any recognized boolean form.
    """
    v = value.strip().lower()
    if v in ("true", "1", "yes"):
        return True
    elif v in ("false", "0", "no"):
        return False
    else:
        raise ConfigError(f"{key} must be a boolean (True/False), \
                          got: {value!r}")


def main() -> None:
    """Parse a config file given as the first argument and print it.

    Expects exactly one command-line argument (the config file path).
    Prints a usage message and exits with status 1 if the argument
    count is wrong or the config fails to parse.
    """
    if len(sys.argv) != 2:
        print("Run with: python3 a_maze_ing.py config.txt", file=sys.stderr)
        sys.exit(1)

    try:
        config = parse_config(sys.argv[1])
    except ConfigError as e:
        print(f"Error: {e}, file=sys.stderr")
        sys.exit(1)

    print(config)


if __name__ == "__main__":
    main()
