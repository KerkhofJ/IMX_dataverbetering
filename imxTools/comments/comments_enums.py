from enum import Enum


class CommentColumns(Enum):
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

    def __str__(self):
        return self.name

    @classmethod
    def label_to_key(cls) -> dict[str, str]:
        return {str(col.value): col.name for col in cls}

    @classmethod
    def key_to_label(cls) -> dict[str, str]:
        return {col.name: str(col.value) for col in cls}
