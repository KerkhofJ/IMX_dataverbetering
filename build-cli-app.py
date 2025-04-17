import subprocess
from pathlib import Path


def build_cli_app():
    script_path = Path("imxCli/cliApp/cliApp.py")
    data_path = Path("data")

    # Ensure paths exist
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    if not data_path.exists():
        raise FileNotFoundError(f"Data folder not found: {data_path}")

    sep = ';' if Path().anchor != '/' else ':'

    command = [
        "pyinstaller",
        str(script_path),
        "--noconfirm",
        "--onefile",
        "--name", "imxCli",
        "--add-data", f"{data_path}{sep}data",
    ]

    print("Running:", " ".join(command))
    subprocess.run(command, check=True)

if __name__ == "__main__":
    build_cli_app()
