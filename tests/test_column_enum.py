import pytest

from imxTools.utils.columnEnum import ColumnEnum


class TestColumns(ColumnEnum):
    object_path = "Full object path in IMX structure"
    comment = "Comment content"
    value = "Original cell value"


def test_str_and_repr():
    assert str(TestColumns.comment) == "comment"
    assert repr(TestColumns.comment) == "<TestColumns.comment: Comment content>"


def test_description_to_header():
    mapping = TestColumns.description_to_header()
    assert mapping == {
        "Full object path in IMX structure": "object_path",
        "Comment content": "comment",
        "Original cell value": "value",
    }


def test_header_to_description():
    mapping = TestColumns.header_to_description()
    assert mapping == {
        "object_path": "Full object path in IMX structure",
        "comment": "Comment content",
        "value": "Original cell value",
    }


def test_description_to_member():
    mapping = TestColumns.description_to_member()
    assert mapping["Comment content"] == TestColumns.comment
    assert mapping["Full object path in IMX structure"] == TestColumns.object_path


def test_from_description():
    assert TestColumns.from_description("Comment content") == TestColumns.comment


def test_from_description_case_insensitive():
    assert (
        TestColumns.from_description("comment content", ignore_case=True)
        == TestColumns.comment
    )
    with pytest.raises(ValueError):
        TestColumns.from_description("comment content", ignore_case=False)


def test_headers_and_names():
    assert set(TestColumns.headers()) == {"object_path", "comment", "value"}
    assert TestColumns.names() == TestColumns.headers()


def test_from_name():
    assert TestColumns.from_name("comment") == TestColumns.comment
    with pytest.raises(ValueError):
        TestColumns.from_name("nonexistent")


def test_to_dict():
    assert TestColumns.to_dict() == {
        "object_path": "Full object path in IMX structure",
        "comment": "Comment content",
        "value": "Original cell value",
    }
