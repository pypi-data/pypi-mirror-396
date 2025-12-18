"""Tests for I18n base class."""

import pytest

from kiarina.i18n import I18n


def test_i18n_class_definition():
    """Test that I18n class can be subclassed."""

    class MyI18n(I18n):
        scope: str = "test.my"
        title: str = "My Title"
        description: str = "My Description"

    # Create instance
    i18n = MyI18n()
    assert i18n.scope == "test.my"
    assert i18n.title == "My Title"
    assert i18n.description == "My Description"


def test_i18n_immutable():
    """Test that I18n instances are immutable."""

    class MyI18n(I18n):
        scope: str = "test.my"
        title: str = "My Title"

    i18n = MyI18n()

    # Should raise error when trying to modify
    with pytest.raises(Exception):  # ValidationError or AttributeError
        i18n.title = "New Title"  # type: ignore


def test_i18n_forbid_extra_fields():
    """Test that extra fields are forbidden."""

    class MyI18n(I18n):
        scope: str = "test.my"
        title: str = "My Title"

    # Should raise error when passing extra fields
    with pytest.raises(Exception):  # ValidationError
        MyI18n(extra_field="value")  # type: ignore
