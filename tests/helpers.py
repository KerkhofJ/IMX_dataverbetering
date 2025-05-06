from collections.abc import Callable, Iterable
from functools import wraps
from pathlib import Path
from pkgutil import ModuleInfo, walk_packages
from types import ModuleType


def packages_in_module(m: ModuleType) -> Iterable[ModuleInfo]:
    return walk_packages(m.__path__, prefix=m.__name__ + ".")  # type: ignore


def package_paths_in_module(m: ModuleType) -> Iterable[str]:
    return [package.name for package in packages_in_module(m)]


def workspace_path(*parts: str) -> Path:
    directory = Path(__file__).parent
    while directory is not None and not any(
        [f for f in directory.iterdir() if f.name.lower() == "pyproject.toml"]
    ):
        directory = directory.parent

    return directory.joinpath(*parts).absolute()


def sample_path(*parts: str) -> str:
    return str(workspace_path("sample_data", *parts))


def assert_path_glob(path: str, glob_pattern: str, expect_present: bool = True) -> None:
    pattern = Path(path).glob(glob_pattern)
    matching_files = list(pattern)

    if expect_present:
        assert matching_files, (
            f"No file found matching the pattern '{glob_pattern}' in {path}"
        )
    else:
        assert not matching_files, (
            f"Unexpected file(s) found matching the pattern '{glob_pattern}' in {path}"
        )


def track_new_files(path_arg: str, extension: str | None = None):
    """
    Decorator to track new files created in a directory during test execution.

    Args:
        path_arg: The name of the argument (or fixture) that contains the output path.
        extension: File extension filter (e.g. "zip"). If None, tracks all new files.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            path: Path = kwargs[path_arg]
            pattern = f"*.{extension.strip('.')}" if extension else "*"
            before = set(path.glob(pattern))

            result = func(*args, **kwargs)

            after = set(path.glob(pattern))
            new_files = after - before

            # Optionally attach new_files to the result, or assert inside the test
            if isinstance(result, dict):
                result["new_files"] = new_files
                return result

            return new_files

        return wrapper

    return decorator
