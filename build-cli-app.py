import subprocess
from pathlib import Path


def build_cli_app():
    script_path = Path("imxCli/cliApp/cliApp.py")
    xsd_12_path = Path("data/xsd-12.0.0")
    xsd_124_path = Path("data/xsd-1.2.4")

    # Ensure paths exist
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    if not xsd_12_path.exists():
        raise FileNotFoundError(f"XSD path not found: {xsd_12_path}")
    if not xsd_124_path.exists():
        raise FileNotFoundError(f"XSD path not found: {xsd_124_path}")

    command = [
        "pyinstaller",
        str(script_path), # "--onefile",
        "--add-data", f"{xsd_12_path}{';' if Path().anchor != '/' else ':'}xsd-12.0.0",
        "--add-data", f"{xsd_124_path}{';' if Path().anchor != '/' else ':'}xsd-1.2.4"
    ]

    print("Running:", " ".join(command))
    subprocess.run(command, check=True)

if __name__ == "__main__":
    build_cli_app()
