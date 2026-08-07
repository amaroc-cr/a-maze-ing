import sys

MANDATORY_KEYS = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}

class ConfigError(Exception):
    pass

def parse_config(path: str)->dict:
    config = {}

    try:
        with open(path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}")
    except OSError as e:
        raise ConfigError(f"Could not read config file: {e}")

    #parsing lines (value will overwrite if repeat assignment) (line can only have 1 "="")
    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if line.count("=") != 1:
            raise ConfigError(f"Line {lineno}: expected one '=', got: {line!r}")

        key, value = line.split("=", 1)
        key = key.strip().upper()
        value = value.strip()

        if not key:
            raise ConfigError(f"Line {lineno}: empty key")
        if not value:
            raise ConfigError(f"Line {lineno}: empty value for key {key}")

        config[key] = value

    #dict validation, parse_coord always called AFTER validating widthe and height!
    missing = MANDATORY_KEYS - config.keys()
    if missing:
            raise ConfigError(f"Missing mandatory key(s): {", ".join(sorted(missing))}")

    config["WIDTH"] = parse_positive_int(config["WIDTH"], "WIDTH")
    config["HEIGHT"] = parse_positive_int(config["HEIGHT"], "HEIGHT")
    config["ENTRY"] = parse_coord(config["ENTRY"], "ENTRY", config["WIDTH"], config["HEIGHT"])
    config["EXIT"] = parse_coord(config["EXIT"], "EXIT", config["WIDTH"], config["HEIGHT"])
    config["PERFECT"] = parse_bool(config["PERFECT"], "PERFECT")

    if config["ENTRY"] == config["EXIT"]:
        raise ConfigError("Entry and exit cannot be the same")

    if not config["OUTPUT_FILE"]:
        raise ConfigError("OUTPUT_FILE cannot be empty")

    return config


def parse_positive_int(value: str, key: str)->int:
    try:
        n = int(value)
    except ValueError:
        raise ConfigError(f"{key} must be an integer, got: {value!r}")
    if n <= 0:
        raise ConfigError(f"{key} must be a positive integer, got: {n}")
    return n


def parse_coord(value: str, key: str, width: int, height: int)->tuple[int, int]:
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(f"{key} must be formatted as x,y, got: {value!r}")
    try:
        x, y = int(parts[0].strip()), int(parts[1].strip())
    except ValueError:
        raise ConfigError(f"{key} coordinates must be integers, got: {value!r}")
    if x < 0 or y < 0:
        raise ConfigError(f"{key} coordinates must be non-negative, got: {value!r}")

    #validate coordinates are within bounds
    if x > width or y > height:
        raise ConfigError(
            f"{key} coordinates are out of maze bounds "
            f"(width)={width}, height={height}"
        )

    return (x, y)


def parse_bool(value: str, key: str)->bool:
    v = value.strip().lower()
    if v in ("true", "1", "yes"):
        return True
    elif v in ("false", "0", "no"):
        return False
    else:
        raise ConfigError(f"{key} must be a boolean (True/False), got: {value!r}")


def main()->None:
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
