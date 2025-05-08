import zipfile
from datetime import datetime, timezone
from pathlib import Path

from imxInsights import ImxContainer, ImxSingleFile
from imxInsights.file.singleFileImx.imxSituationEnum import ImxSituationEnum


def clear_directory(directory: Path) -> None:
    if directory.exists() and directory.is_dir():
        for item in directory.iterdir():
            if item.is_file() and item.name != "generated.content":
                item.unlink()
            elif item.is_dir():
                clear_directory(item)
                item.rmdir()


def load_imxinsights_container_or_file(path: Path, situation: ImxSituationEnum | None):
    if path.suffix == ".zip":
        return ImxContainer(path)
    elif path.suffix == ".xml":
        if not situation:
            raise ValueError(f"Situation must be specified for single IMX file: {path}")
        imx = ImxSingleFile(path)
        return {
            ImxSituationEnum.InitialSituation: imx.initial_situation,
            ImxSituationEnum.NewSituation: imx.new_situation,
            ImxSituationEnum.Situation: imx.situation,
        }.get(situation)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")


def zip_folder(folder: Path, output_zip: Path) -> None:
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in folder.rglob("*"):
            zipf.write(file_path, file_path.relative_to(folder))


def create_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_paths(*args):
    return [Path(a) if isinstance(a, str) else a for a in args]


def snake_to_camel(snake_str: str) -> str:
    return ''.join(word.capitalize() for word in snake_str.split('_'))
