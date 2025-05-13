import pytest

from imxTools.utils.columnEnum import ColumnEnum  # adjust path if needed


class DummyColumns(ColumnEnum):
    name = "Name of the person"
    age = "Age in years"
    city = "City of residence"


def test_str_returns_enum_name():
    assert str(DummyColumns.name) == "name"
    assert str(DummyColumns.age) == "age"


def test_label_to_key():
    label_to_key = DummyColumns.label_to_key()
    assert label_to_key["Name of the person"] == "name"
    assert label_to_key["Age in years"] == "age"


def test_key_to_label():
    key_to_label = DummyColumns.key_to_label()
    assert key_to_label["name"] == "Name of the person"
    assert key_to_label["age"] == "Age in years"


def test_value_to_member():
    value_map = DummyColumns.value_to_member()
    assert value_map["Name of the person"] == DummyColumns.name
    assert value_map["City of residence"] == DummyColumns.city


def test_from_label_valid():
    member = DummyColumns.from_label("City of residence")
    assert member == DummyColumns.city


def test_from_label_invalid():
    with pytest.raises(ValueError, match="No column found for label: Unknown Label"):
        DummyColumns.from_label("Unknown Label")
