from collections.abc import Iterable
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
        assert matching_files, f"No file found matching the pattern '{glob_pattern}' in {path}"
    else:
        assert not matching_files, f"Unexpected file(s) found matching the pattern '{glob_pattern}' in {path}"

