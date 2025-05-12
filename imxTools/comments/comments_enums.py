from utils.columnEnum import ColumnEnum


class CommentColumns(ColumnEnum):
    object_path = "Full object path in IMX structure"
    object_puic = "PUIC (unique identifier) of the object"
    change_status = "Change status of the object"
    geometry_status = "Geometry change status"
    link = "Clickable Excel hyperlink to the comment"
    imx_path = "Field or path of the IMX attribute"
    value = "Current value in cell"
    comment = "Comment content"
    comment_reason = "Comment reason"
    color = "Cell background color"
    comment_sheet_name = "Name of sheet with the comment"
    comment_row = "Row number of the comment"
    comment_column = "Column number of the comment"

