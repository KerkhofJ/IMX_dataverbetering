import os
import platform
import re
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

from imxTools import __version__ as imxTools_version
from imxInsights import __version__ as imxInsights_version


def extract_version(init_file: Path = Path("imxTools/__init__.py")) -> str:
    content = init_file.read_text()
    match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError(f"Version not found in {init_file}")
    return match.group(1)


def insert_readable_metadata(file_path: Path):
    metadata = (
        f"# **imxTools CLI App** (v{imxTools_version})  \n"
        f"**Build Date**: {date.today().isoformat()}  \n"
        f"**imxInsights Version**: {imxInsights_version}  \n\n"
        f"---\n\n"
        f"> **Disclaimer**: This software is provided \"as is\", without warranty of any kind, "
        f"express or implied, including but not limited to the warranties of merchantability, "
        f"fitness for a particular purpose and noninfringement. In no event shall the authors or "
        f"copyright holders be liable for any claim, damages or other liability, whether in an "
        f"action of contract, tort or otherwise, arising from, out of or in connection with the "
        f"software or the use or other dealings in the software.  \n\n"
        f"---\n\n"
    )
    original_content = file_path.read_text(encoding="utf-8")
    file_path.write_text(metadata + original_content, encoding="utf-8")


def _get_pyinstaller_command(script_path: Path, dist_path: Path, exe_name: str, data_path: Path) -> list[str]:
    sep = ';' if os.name == 'nt' else ':'
    return [
        "pyinstaller",
        str(script_path),
        "--noconfirm",
        "--clean",
        "--distpath", str(dist_path),
        "--name", exe_name,
        "--add-data", f"{data_path}{sep}data",
        "--hidden-import=shellingham.nt",
        "--hidden-import=shellingham.posix",
    ]


def _generate_readme(script_path: Path, readme_path: Path):
    typer_cmd = [
        sys.executable,
        "-m", "typer",
        str(script_path),
        "utils",
        "docs",
        "--output", str(readme_path),
    ]
    subprocess.run(typer_cmd, check=True)
    insert_readable_metadata(readme_path)


def zip_result(folder_path: Path, version: str, system: str):
    zip_name = f"imxTools-{version}-{system}.zip"
    zip_path = folder_path.parent / zip_name
    print(f"Creating ZIP: {zip_path}")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in folder_path.rglob("*"):
            zipf.write(file, arcname=file.relative_to(folder_path))

    print(f"Packaged: {zip_path}")


def build_cli_app():
    script_path = Path("cliApp/cliApp.py")
    data_path = Path("data")
    dist_path = Path("dist")
    exe_name = "open-imx"

    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    if not data_path.exists():
        raise FileNotFoundError(f"Data folder not found: {data_path}")

    version = extract_version()
    command = _get_pyinstaller_command(script_path, dist_path, exe_name, data_path)

    print("Running:", " ".join(command))
    try:
        subprocess.run(command, check=True)

        exe_suffix = ".exe" if os.name == "nt" else ""
        folder_path = dist_path / exe_name
        exe_path = folder_path / f"{exe_name}{exe_suffix}"

        if not exe_path.exists():
            raise FileNotFoundError(f"Executable not found: {exe_path}")
        print(f"\nBuilt: {exe_path}")

        readme_path = folder_path / "README.md"
        _generate_readme(script_path, readme_path)
        print(f"Added metadata to README: {readme_path}")

        zip_result(folder_path, version, platform.system().lower())

    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed: {e}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    build_cli_app()
