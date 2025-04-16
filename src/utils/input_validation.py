from pathlib import Path


class InputValidationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("\n".join(errors))


def validate_process_input(imx_input: Path, excel_input: Path, out_path: Path) -> tuple[Path, Path]:
    input_errors = []

    if not imx_input.exists():
        input_errors.append(f"❌ imx_input does not exist: {imx_input}")
    elif imx_input.suffix.lower() != '.xml':
        input_errors.append(f"❌ imx_input is not an xml file: {imx_input}")

    if not excel_input.exists():
        input_errors.append(f"❌ excel_input does not exist: {excel_input}")
    elif excel_input.suffix.lower() not in ['.xlsx', '.xlsm']:
        input_errors.append(f"❌ excel_input is not a valid Excel file: {excel_input}")

    imx_output = out_path / f"{imx_input.stem}-processed{imx_input.suffix}"
    excel_output = out_path / f"{excel_input.stem}-processed{excel_input.suffix}"

    if imx_output.exists():
        input_errors.append(f"❌ imx_output already exists: {imx_output}")
    if excel_output.exists():
        input_errors.append(f"❌ excel_output already exists: {excel_output}")

    if input_errors:
        raise InputValidationError(input_errors)

    return imx_output, excel_output
