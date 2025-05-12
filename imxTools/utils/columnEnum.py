from enum import Enum


#TODO: if py3.10 = eol we should consider using StrEnum
class ColumnEnum(Enum):

    def __str__(self):
        return self.name

    @classmethod
    def label_to_key(cls) -> dict[str, str]:
        return {str(col.value): col.name for col in cls}

    @classmethod
    def key_to_label(cls) -> dict[str, str]:
        return {col.name: str(col.value) for col in cls}

    @classmethod
    def value_to_member(cls) -> dict[str, 'ColumnEnum']:
        return {str(col.value): col for col in cls}

    @classmethod
    def from_label(cls, label: str) -> 'ColumnEnum':
        for member in cls:
            if str(member.value) == label:
                return member
        raise ValueError(f"No column found for label: {label}")
