import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from apps.build_helpers import (
    insert_readable_metadata,
    zip_result,
    remove_folder_safely,
)
from imxTools import __version__ as app_version

# App constants
EXECUTABLE_NAME = "imx-tools-cli"
APP_FOLDER_NAME = f"{EXECUTABLE_NAME}-{app_version}-windows"
ENTRY_FILE = Path("apps/cli/main.py")

# Paths
DATA_FOLDER = Path("data")
DIST_ROOT = Path("dist")
FINAL_APP_FOLDER = DIST_ROOT / APP_FOLDER_NAME
BUILD_FOLDER = Path(".build_cli_app")

# Cleanup flags
CLEAN_BUILD_FOLDER = True
CLEANUP = True

if CLEAN_BUILD_FOLDER and BUILD_FOLDER.exists():
    print("🧹 Cleaning build folder...")
    shutil.rmtree(BUILD_FOLDER)


def _get_pyinstaller_command(script_path: Path, output_folder_name: str, data_path: Path) -> list[str]:
    sep = ';' if os.name == 'nt' else ':'
    return [
        "pyinstaller",
        str(script_path),
        "--noconfirm",
        "--clean",
        "--name", output_folder_name,
        "--distpath", str(DIST_ROOT),
        "--workpath", str(BUILD_FOLDER),
        "--add-data", f"{data_path}{sep}{data_path.name}",
        "--hidden-import=shellingham.nt",
        "--hidden-import=shellingham.posix",
    ]


def build_cli_app():
    if not ENTRY_FILE.exists():
        raise FileNotFoundError(f"❌ Script not found: {ENTRY_FILE}")
    if not DATA_FOLDER.exists():
        raise FileNotFoundError(f"❌ Data folder not found: {DATA_FOLDER}")

    print(f"🚀 Building CLI app: {APP_FOLDER_NAME}")

    remove_folder_safely(FINAL_APP_FOLDER)
    remove_folder_safely(BUILD_FOLDER)
    FINAL_APP_FOLDER.mkdir(parents=True, exist_ok=True)
    BUILD_FOLDER.mkdir(parents=True, exist_ok=True)

    command = _get_pyinstaller_command(ENTRY_FILE, APP_FOLDER_NAME, DATA_FOLDER)
    print(f"🛠️ Running PyInstaller...\n{' '.join(command)}")

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        for line in process.stdout:
            print(line, end="")

        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)

        # List contents of FINAL_APP_FOLDER
        print(f"📂 Scanning folder contents in: {FINAL_APP_FOLDER}")
        for f in FINAL_APP_FOLDER.rglob("*"):
            print(" -", f.relative_to(FINAL_APP_FOLDER))

        # Look for the executable inside FINAL_APP_FOLDER
        exe_files = list(FINAL_APP_FOLDER.glob("*.exe"))
        if not exe_files:
            raise FileNotFoundError(f"❌ No .exe file found in {FINAL_APP_FOLDER}. Check PyInstaller output.")
        original_exe_path = exe_files[0]

        # Rename it to remove version and OS
        final_exe_path = FINAL_APP_FOLDER / f"{EXECUTABLE_NAME}.exe"
        original_exe_path.rename(final_exe_path)

        print(f"✅ Renamed executable to: {final_exe_path}")

        # Generate README
        readme_path = FINAL_APP_FOLDER / "README.md"
        insert_readable_metadata(readme_path, APP_FOLDER_NAME)
        print(f"📘 Added metadata to README: {readme_path}")

        # Zip it
        zip_result(FINAL_APP_FOLDER, app_version, platform.system().lower(), EXECUTABLE_NAME, DIST_ROOT)
        print(f"🎉 CLI app ready at: {FINAL_APP_FOLDER}")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    build_cli_app()

    if CLEANUP and BUILD_FOLDER.exists():
        print("🧹 Cleaning build folder...")
        shutil.rmtree(BUILD_FOLDER)
