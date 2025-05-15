import pytest

from imxTools.utils.columnEnum import ColumnEnum


class CustomColumnEnum(ColumnEnum):
    object_path = "Full object path in IMX structure"
    comment = "Comment content"
    value = "Original cell value"


def test_str_and_repr():
    assert str(CustomColumnEnum.comment) == "comment"
    assert repr(CustomColumnEnum.comment) == "<CustomColumnEnum.comment: Comment content>"


def test_description_to_header():
    mapping = CustomColumnEnum.description_to_header()
    assert mapping == {
        "Full object path in IMX structure": "object_path",
        "Comment content": "comment",
        "Original cell value": "value",
    }


def test_header_to_description():
    mapping = CustomColumnEnum.header_to_description()
    assert mapping == {
        "object_path": "Full object path in IMX structure",
        "comment": "Comment content",
        "value": "Original cell value",
    }


def test_description_to_member():
    mapping = CustomColumnEnum.description_to_member()
    assert mapping["Comment content"] == CustomColumnEnum.comment
    assert mapping["Full object path in IMX structure"] == CustomColumnEnum.object_path


def test_from_description():
    assert CustomColumnEnum.from_description("Comment content") == CustomColumnEnum.comment


def test_from_description_case_insensitive():
    assert (
            CustomColumnEnum.from_description("comment content", ignore_case=True)
            == CustomColumnEnum.comment
    )
    with pytest.raises(ValueError):
        CustomColumnEnum.from_description("comment content", ignore_case=False)


def test_headers_and_names():
    assert set(CustomColumnEnum.headers()) == {"object_path", "comment", "value"}
    assert CustomColumnEnum.names() == CustomColumnEnum.headers()


def test_from_name():
    assert CustomColumnEnum.from_name("comment") == CustomColumnEnum.comment
    with pytest.raises(ValueError):
        CustomColumnEnum.from_name("nonexistent")


def test_to_dict():
    assert CustomColumnEnum.to_dict() == {
        "object_path": "Full object path in IMX structure",
        "comment": "Comment content",
        "value": "Original cell value",
    }
