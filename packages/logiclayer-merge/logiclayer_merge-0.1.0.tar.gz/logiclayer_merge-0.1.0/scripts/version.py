from pathlib import Path

import tomli


def read_version() -> str:
    # Load the version from pyproject.toml
    with Path("pyproject.toml").open("rb") as fileio:
        pyproject = tomli.load(fileio)
    return pyproject["project"]["version"]


def write_in_library() -> None:
    version = read_version()

    file_path = Path("src/logiclayer_merge", "__init__.py")

    with file_path.open() as f:
        lines = f.readlines()

    with file_path.open("w") as f:
        for line in lines:
            if line.startswith("__version__"):
                f.write(f'__version__ = "{version}"\n')
            else:
                f.write(line)

    print(f"Version updated in __init__.py to {version}")


if __name__ == "__main__":
    write_in_library()