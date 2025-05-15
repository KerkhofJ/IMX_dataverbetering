from pathlib import Path

from imxTools.comments.comments_extractor import extract_comments_to_new_sheet
from imxTools.comments.comments_replacer import apply_comments_from_issue_list


def test_extract_comments_to_new_sheet(diff_report, output_path):
    extract_comments_to_new_sheet(
        diff_report, f"{Path(output_path) / 'comment-list.xlsx'}", overwrite=True
    )


def test_extract_comments_to_new_sheet_with_add_to_wb(diff_report, clean_output_path):
    # TODO: comment sheet seems not to be on the second sheet
    extract_comments_to_new_sheet(
        diff_report,
        f"{Path(clean_output_path) / 'copied-with-comments.xlsx'}",
        add_to_wb=True,
        overwrite=True,
    )


def test_extract_comments_to_new_sheet_without_overwrite(diff_report):
    extract_comments_to_new_sheet(diff_report, add_to_wb=True, overwrite=True)


def test_apply_comments_to_new_file(diff_report_edit, comment_list, output_path):
    # TODO: comment sheet seems not to be on the second sheet
    # TODO: named styles are not only background fill
    # TODO: seems to add it to the original file
    apply_comments_from_issue_list(
        issue_list_path=comment_list,
        new_diff_path=diff_report_edit,
        output_path=f"{Path(output_path) / 'updated_diff_with_comments.xlsx'}",
    )
