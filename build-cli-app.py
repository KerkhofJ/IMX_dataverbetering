import subprocess
import os
import platform
from pathlib import Path
import re
import sys
import zipfile


def extract_version():
    init_path = Path("imxTools/__init__.py")
    content = init_path.read_text()
    match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError("Version not found in imxTools/__init__.py")
    return match.group(1)


def build_cli_app():
    script_path = Path("imxTools/cliApp/cliApp.py")
    data_path = Path("data")

    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    if not data_path.exists():
        raise FileNotFoundError(f"Data folder not found: {data_path}")

    version = extract_version()
    exe_name = f"imxTools"

    sep = ';' if os.name == 'nt' else ':'

    command = [
        "pyinstaller",
        str(script_path),
        "--noconfirm",
        "--clean",
        "--distpath", "dist",
        "--name", exe_name,
        "--add-data", f"{data_path}{sep}data",
    ]

    print("Running:", " ".join(command))
    try:
        subprocess.run(command, check=True)

        # One-folder app path
        folder_path = Path("dist") / exe_name
        exe_filename = exe_name + (".exe" if os.name == "nt" else "")

        exe_path = folder_path / exe_filename
        if not exe_path.exists():
            raise FileNotFoundError(f"Executable not found at: {exe_path}")

        print(f"\nBuilt: {exe_path}")
        system = platform.system().lower()
        zip_result(folder_path, version, system)
    except subprocess.CalledProcessError as e:
        print(f"\nPyInstaller failed: {e}")
        sys.exit(e.returncode)


def zip_result(folder_path: Path, version: str, system: str):
    zip_name = f"imxTools-{version}-{system}.zip"
    zip_path = folder_path.parent / zip_name
    print(f"Creating ZIP: {zip_path}")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in folder_path.rglob("*"):
            zipf.write(file, arcname=file.relative_to(folder_path))
    print(f"Packaged: {zip_path}")


if __name__ == "__main__":
    build_cli_app()
