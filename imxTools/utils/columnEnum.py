#TODO: if py3.10 = eol we should consider using StrEnum
from enum import Enum


class ColumnEnum(Enum):
    """
    Base Enum class for column definitions with human-readable labels.
    Provides utility methods to convert between enum names, values, and members.
    """

    def __str__(self):
        """
        Return the name of the enum member when converted to a string.
        This ensures `str(ColumnEnum.member)` gives 'member' instead of the value.
        """
        return self.name

    @classmethod
    def label_to_key(cls) -> dict[str, str]:
        """
        Return a mapping from human-readable labels (enum values) to enum keys (names).

        Example:
            {'Full object path in IMX structure': 'object_path'}
        """
        return {str(col.value): col.name for col in cls}

    @classmethod
    def key_to_label(cls) -> dict[str, str]:
        """
        Return a mapping from enum keys (names) to human-readable labels (values).

        Example:
            {'object_path': 'Full object path in IMX structure'}
        """
        return {col.name: str(col.value) for col in cls}

    @classmethod
    def value_to_member(cls) -> dict[str, 'ColumnEnum']:
        """
        Return a mapping from human-readable labels (values) to enum members.

        Example:
            {'Full object path in IMX structure': CommentColumns.object_path}
        """
        return {str(col.value): col for col in cls}

    @classmethod
    def from_label(cls, label: str) -> 'ColumnEnum':
        """
        Return the enum member corresponding to a given human-readable label (value).

        Raises:
            ValueError: If no matching label is found.

        Example:
            CommentColumns.from_label("Comment content") -> CommentColumns.comment
        """
        for member in cls:
            if str(member.value) == label:
                return member
        raise ValueError(f"No column found for label: {label}")
