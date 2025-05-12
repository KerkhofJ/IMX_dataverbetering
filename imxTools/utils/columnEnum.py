from enum import Enum


class ColumnEnum(Enum):

    def __str__(self):
        return self.name

    @classmethod
    def label_to_key(cls) -> dict[str, str]:
        return {str(col.value): col.name for col in cls}

    @classmethod
    def key_to_label(cls) -> dict[str, str]:
        return {col.name: str(col.value) for col in cls}



