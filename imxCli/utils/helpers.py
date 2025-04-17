from pathlib import Path


def clear_directory(directory: Path):
    if directory.exists() and directory.is_dir():
        for item in directory.iterdir():
            if item.is_file():
                item.unlink()  # Remove file
            elif item.is_dir():
                clear_directory(item)  # Recursively clear subdirectory
                item.rmdir()  # Remove empty subdirectory

