import os
import shutil

from imxInsights.utils.report_helpers import REVIEW_STYLES
from openpyxl import Workbook, load_workbook
from openpyxl.cell import Cell, MergedCell
from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet


def get_cell_background_color(cell) -> str | None:
    if cell.fill and cell.fill.fgColor and cell.fill.fgColor.type == "rgb":
        return cell.fill.fgColor.rgb[-6:]
    return None


def get_column_indices(ws: Worksheet, header_row: int) -> dict[str, int | None]:
    keys = ["@puic", "path", "status", "geometry_status"]
    return {
        key: next(
            (
                col
                for col in range(1, ws.max_column + 1)
                if ws[f"{get_column_letter(col)}{header_row}"].value == key
            ),
            None,
        )
        for key in keys
    }


def get_cell_context(ws, row_idx, columns):
    def get(col_key):
        col = columns.get(col_key)
        return ws.cell(row=row_idx, column=col).value if col else None

    return {
        "Puic": get("@puic"),
        "ObjectPath": get("path"),
        "ChangeStatus": get("status"),
        "GeometryStatus": get("geometry_status"),
    }


def build_comment_dict(context, cell, header, sheet_name, comment_text) -> dict:
    return {
        "Sheet": sheet_name,
        "Puic": context["Puic"],
        "Header": header,
        "Value": str(cell.value),
        "Comment": comment_text,
        "CellAddress": cell.coordinate,
        "Color": get_cell_background_color(cell),
        "ObjectPath": context["ObjectPath"],
        "ChangeStatus": context["ChangeStatus"],
        "GeometryStatus": context["GeometryStatus"],
        "CommentSheetName": sheet_name,
        "CommentRow": cell.row,
        "CommentColumn": cell.column,
    }


def handle_header_comment(
    cell: Cell | MergedCell,
    ws: Worksheet,
    header_value: str,
    columns: dict[str, int | None],
    sheet_name: str,
    header_row: int,
) -> tuple[list[dict[str, str | int | None]], list[str]]:
    comments: list[dict[str, str | int | None]] = []
    inherited_cells: list[str] = []

    if get_cell_background_color(cell) == "FFFFFF":
        return comments, inherited_cells

    for row_idx in range(header_row + 1, ws.max_row + 1):
        if cell.column is None:
            continue
        target_cell = ws.cell(row=row_idx, column=cell.column)

        if target_cell.comment or not target_cell.value:
            continue
        color = get_cell_background_color(target_cell)
        if color and color != "000000":
            context = get_cell_context(ws, row_idx, columns)
            if cell.comment:
                comments.append(
                    build_comment_dict(
                        context, target_cell, header_value, sheet_name, cell.comment.text
                    )
                )
                inherited_cells.append(target_cell.coordinate)
    return comments, inherited_cells


def handle_data_comment(cell, ws, header_value, columns, sheet_name):
    context = get_cell_context(ws, cell.row, columns)
    return [
        build_comment_dict(context, cell, header_value, sheet_name, cell.comment.text)
    ]


def write_comments_sheet(wb, comments, overwrite=False):
    if "Comments" in wb.sheetnames:
        if overwrite:
            del wb["Comments"]
        else:
            raise ValueError(
                "Sheet 'Comments' already exists. Set overwrite=True to overwrite."
            )

    ws = wb.create_sheet("Comments")
    wb._sheets.insert(1, wb._sheets.pop(wb._sheets.index(ws)))

    ws.append(
        [
            "ObjectPath",
            "Puic",
            "ChangeStatus",
            "GeometryStatus",
            "Link",
            "ImxPath",
            "Value",
            "Comment",
            "Color",
            "CommentSheetName",
            "CommentRow",
            "CommentColumn",
        ]
    )

    color_to_status = {v: k for k, v in REVIEW_STYLES.items()}

    for comment in comments:
        link_text = color_to_status.get(comment["Color"], "link")
        link = f'=HYPERLINK("#\'{comment["Sheet"]}\'!{comment["CellAddress"]}", "{link_text}")'
        row = [
            comment["ObjectPath"],
            comment["Puic"],
            comment["ChangeStatus"],
            comment["GeometryStatus"],
            link,
            comment["Header"],
            comment["Value"],
            comment["Comment"],
            comment["Color"],
            comment["CommentSheetName"],
            comment["CommentRow"],
            comment["CommentColumn"],
        ]
        ws.append(row)
        if comment["Color"]:
            ws[f"E{ws.max_row}"].fill = PatternFill(
                start_color=comment["Color"],
                end_color=comment["Color"],
                fill_type="solid",
            )

    ws.freeze_panes = "A2"

    for col in range(1, ws.max_column + 1):
        col_cells = next(ws.iter_cols(min_col=col, max_col=col))
        max_len = max(len(str(cell.value) or "") for cell in col_cells) + 4
        ws.column_dimensions[get_column_letter(col)].width = max_len


def extract_comments_to_new_sheet(
    file_path, output_path=None, header_row=1, add_to_wb=False, overwrite=False
):
    if not output_path and not add_to_wb:
        raise ValueError("When adding to an existing workbook, provide an output path.")

    target_path = output_path if output_path and add_to_wb else file_path
    if output_path and add_to_wb:
        if os.path.exists(output_path) and not overwrite:
            raise FileExistsError(
                f"File '{output_path}' already exists. Set overwrite=True."
            )

        shutil.copyfile(file_path, output_path)

    wb = load_workbook(target_path, data_only=True)
    all_comments, inherited_cells = [], set()

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        columns = get_column_indices(ws, header_row)

        for row in ws.iter_rows():
            for cell in row:
                if not cell.column:
                    continue
                header_cell = ws[f"{get_column_letter(cell.column)}{header_row}"]
                header_value = header_cell.value if header_cell else None

                if cell.comment:
                    if cell.row == header_row and isinstance(header_value, str):
                        comments, inherited = handle_header_comment(
                            cell, ws, header_value, columns, sheet_name, header_row
                        )
                        all_comments.extend(comments)
                        inherited_cells.update(inherited)
                    elif cell.row != header_row:
                        all_comments.extend(
                            handle_data_comment(
                                cell, ws, header_value or "", columns, sheet_name
                            )
                        )
                else:
                    color = get_cell_background_color(cell)
                    if (
                        cell.row > header_row
                        and color in REVIEW_STYLES.values()
                        and cell.value
                        and cell.coordinate not in inherited_cells
                    ):
                        context = get_cell_context(ws, cell.row, columns)
                        all_comments.append(
                            build_comment_dict(
                                context, cell, header_value, sheet_name, ""
                            )
                        )

    if add_to_wb:
        if os.path.exists(file_path) and not overwrite:
            raise FileExistsError(
                f"File '{file_path}' already exists. Set overwrite=True."
            )

        write_comments_sheet(wb, all_comments, overwrite)
        wb.save(target_path)
        print(
            f"Comments sheet written to '{target_path}' (in-place={target_path == file_path})."
        )

    else:
        if output_path and os.path.exists(output_path) and not overwrite:
            raise FileExistsError(
                f"File '{output_path}' already exists. Set overwrite=True."
            )
        wb_new = Workbook()
        active_sheet = wb_new.active
        if isinstance(active_sheet, Worksheet):
            wb_new.remove(active_sheet)

        write_comments_sheet(wb_new, all_comments, overwrite)
        output_path = output_path or file_path.replace(".xlsx", "_comments.xlsx")
        wb_new.save(output_path)
        print(
            f"Comments extracted successfully to '{output_path}' in sheet 'Comments'."
        )


# TODO: move below to logic test

extract_comments_to_new_sheet(
    "./20250430_202130-diff.xlsx", "./comment-list.xlsx", overwrite=True
)

# extract_comments_to_new_sheet(
#     "./20250430_202130-diff.xlsx",
#     "./copied-with-comments.xlsx",
#     add_to_wb=True,
#     overwrite=True,
# )
#
# extract_comments_to_new_sheet(
#     "./20250430_202130-diff.xlsx", add_to_wb=True, overwrite=True
# )
