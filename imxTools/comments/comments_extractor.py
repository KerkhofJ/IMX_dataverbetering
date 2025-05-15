import os
import shutil
from pathlib import Path
from typing import Optional, Union

from openpyxl import Workbook, load_workbook
from openpyxl.cell import Cell, MergedCell
from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from imxInsights.utils.report_helpers import REVIEW_STYLES
from imxTools.comments.comments_enums import CommentColumns

ISSUE_LIST_SHEET_NAME = "comments"
CellType = Union[Cell, MergedCell]
CommentDict = dict[str, Union[str, int, None]]


def get_cell_background_color(cell: CellType) -> Optional[str]:
    if cell.fill and cell.fill.fgColor and cell.fill.fgColor.type == "rgb":
        return cell.fill.fgColor.rgb[-6:]
    return None


def get_column_indices(ws: Worksheet, header_row: int) -> dict[str, Optional[int]]:
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


def get_cell_context(ws: Worksheet, row_idx: int, columns: dict[str, Optional[int]]) -> dict[str, Optional[str]]:
    def get(col_key: str) -> Optional[str]:
        col = columns.get(col_key)
        val = ws.cell(row=row_idx, column=col).value if col else None
        return str(val) if val is not None else None

    return {
        CommentColumns.object_puic: get("@puic"),
        CommentColumns.object_path: get("path"),
        CommentColumns.change_status: get("status"),
        CommentColumns.geometry_status: get("geometry_status"),
    }


def build_comment_dict(
    context: dict[str, Optional[str]],
    cell: CellType,
    header: str,
    sheet_name: str,
    comment_text: str,
    comment_row: Optional[int] = None,
) -> CommentDict:
    return {
        CommentColumns.comment_sheet_name: sheet_name,
        CommentColumns.object_puic: context[CommentColumns.object_puic],
        CommentColumns.header_value: header,
        CommentColumns.value: str(cell.value) if cell.value is not None else "",
        CommentColumns.comment: comment_text,
        "CellAddress": cell.coordinate,
        CommentColumns.cell_bg_color: get_cell_background_color(cell),
        CommentColumns.object_path: context[CommentColumns.object_path],
        CommentColumns.change_status: context[CommentColumns.change_status],
        CommentColumns.geometry_status: context[CommentColumns.geometry_status],
        CommentColumns.comment_row: comment_row if comment_row is not None else cell.row,
        CommentColumns.comment_column: cell.column,
    }


def handle_header_comment(
    cell: CellType,
    ws: Worksheet,
    header_value: str,
    columns: dict[str, Optional[int]],
    sheet_name: str,
    header_row: int,
) -> tuple[list[CommentDict], list[str]]:
    comments, inherited_cells = [], []

    if get_cell_background_color(cell) == "FFFFFF":
        return comments, inherited_cells

    for row_idx in range(header_row + 1, ws.max_row + 1):
        target_cell = ws.cell(row=row_idx, column=cell.column)
        if target_cell.comment or not target_cell.value:
            continue
        color = get_cell_background_color(target_cell)
        if color and color != "000000":
            context = get_cell_context(ws, row_idx, columns)
            if cell.comment:
                comments.append(
                    build_comment_dict(context, target_cell, header_value, sheet_name, cell.comment.text, header_row)
                )
                inherited_cells.append(target_cell.coordinate)
    return comments, inherited_cells


def handle_data_comment(
    cell: CellType,
    ws: Worksheet,
    header_value: str,
    columns: dict[str, Optional[int]],
    sheet_name: str,
) -> list[CommentDict]:
    context = get_cell_context(ws, cell.row, columns)
    return [
        build_comment_dict(
            context,
            cell,
            header_value,
            sheet_name,
            cell.comment.text if cell.comment else "",
        )
    ]


def write_comments_sheet(
    wb: Workbook,
    comments: list[CommentDict],
    overwrite: bool = False,
) -> None:
    if ISSUE_LIST_SHEET_NAME in wb.sheetnames:
        if overwrite:
            del wb[ISSUE_LIST_SHEET_NAME]
        else:
            raise ValueError(f"Sheet '{ISSUE_LIST_SHEET_NAME}' already exists. Set overwrite=True to overwrite.")

    ws_comments = wb.create_sheet(ISSUE_LIST_SHEET_NAME)
    worksheets = wb.worksheets
    worksheets.remove(ws_comments)
    insert_at = next((i + 1 for i, ws in enumerate(worksheets) if ws.title == "info"), 0)
    worksheets.insert(insert_at, ws_comments)

    ws_comments.append(CommentColumns.names())
    ws_comments.auto_filter.ref = f"A1:{get_column_letter(ws_comments.max_column)}1"

    color_to_status = {v: k for k, v in REVIEW_STYLES.items()}
    for comment in comments:
        link_text = color_to_status.get(str(comment[CommentColumns.cell_bg_color]), "link")
        link = f'=HYPERLINK("#\'{comment[CommentColumns.comment_sheet_name]}\'!{comment["CellAddress"]}", "{link_text}")'
        row = [
            comment[CommentColumns.object_path],
            comment[CommentColumns.object_puic],
            comment[CommentColumns.change_status],
            comment[CommentColumns.geometry_status],
            link,
            comment[CommentColumns.header_value],
            comment[CommentColumns.value],
            comment[CommentColumns.comment],
            comment[CommentColumns.cell_bg_color],
            comment[CommentColumns.comment_sheet_name],
            comment[CommentColumns.comment_row],
            comment[CommentColumns.comment_column],
        ]
        ws_comments.append(row)
        color = str(comment[CommentColumns.cell_bg_color]) or None
        if color:
            ws_comments[f"E{ws_comments.max_row}"].fill = PatternFill(start_color=color, end_color=color, fill_type="solid")

    ws_comments.freeze_panes = "A2"

    for col in range(1, ws_comments.max_column + 1):
        col_cells = next(ws_comments.iter_cols(min_col=col, max_col=col))
        max_len = max(len(str(cell.value) or "") for cell in col_cells) + 4
        ws_comments.column_dimensions[get_column_letter(col)].width = max_len


def extract_comments_to_new_sheet(
    file_path: Union[str, Path],
    output_path: Optional[str] = None,
    header_row: int = 1,
    add_to_wb: bool = False,
    overwrite: bool = False,
) -> None:
    if not output_path and not add_to_wb:
        raise ValueError("When adding to an existing workbook, provide an output path.")

    target_path = output_path if output_path and add_to_wb else file_path
    if output_path and add_to_wb:
        if os.path.exists(output_path) and not overwrite:
            raise FileExistsError(f"File '{output_path}' already exists. Set overwrite=True.")
        shutil.copyfile(file_path, output_path)

    wb = load_workbook(target_path, data_only=True)
    all_comments: list[CommentDict] = []
    inherited_cells: set[str] = set()

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        columns = get_column_indices(ws, header_row)

        for row in ws.iter_rows():
            for cell in row:
                header_cell = ws[f"{get_column_letter(cell.column)}{header_row}"]
                header_value = str(header_cell.value or "")

                if cell.comment:
                    if cell.row == header_row:
                        comments, inherited = handle_header_comment(cell, ws, header_value, columns, sheet_name, header_row)
                        all_comments.extend(comments)
                        inherited_cells.update(inherited)
                    else:
                        all_comments.extend(handle_data_comment(cell, ws, header_value, columns, sheet_name))
                else:
                    color = get_cell_background_color(cell)
                    if cell.row > header_row and color in REVIEW_STYLES.values() and cell.value and cell.coordinate not in inherited_cells:
                        context = get_cell_context(ws, cell.row, columns)
                        all_comments.append(build_comment_dict(context, cell, header_value, sheet_name, ""))

    if add_to_wb:
        if os.path.exists(file_path) and not overwrite:
            raise FileExistsError(f"File '{file_path}' already exists. Set overwrite=True.")
        write_comments_sheet(wb, all_comments, overwrite)
        wb.save(target_path)
        print(f"Comments sheet written to '{target_path}' (in-place={target_path == file_path}).")
    else:
        output_path = output_path or str(file_path).replace(".xlsx", "_comments.xlsx")
        wb_new = Workbook()
        wb_new.remove(wb_new.active)
        write_comments_sheet(wb_new, all_comments, overwrite)
        wb_new.save(output_path)
        print(f"Comments extracted successfully to '{output_path}' in sheet '{ISSUE_LIST_SHEET_NAME}'.")