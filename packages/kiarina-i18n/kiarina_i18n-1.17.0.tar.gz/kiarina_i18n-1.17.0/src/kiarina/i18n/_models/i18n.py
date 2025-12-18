"""Base class for i18n definitions."""

from pydantic import BaseModel, Field


class I18n(BaseModel):
    """
    Base class for i18n definitions.

    This class provides a type-safe way to define translation keys and default values.
    Subclasses should define a scope and translation keys as class fields.

    Example:
        ```python
        from kiarina.i18n import I18n, get_i18n

        class MyI18n(I18n):
            scope: str = "my.module"

            title: str = "My Title"
            description: str = "My Description"

        # Get translated instance
        t = get_i18n(MyI18n, "ja")
        print(t.title)  # Translated title
        ```
    """

    scope: str = Field(..., description="Translation scope (e.g., 'my.module')")

    model_config = {
        "frozen": True,  # Make instances immutable
        "extra": "forbid",  # Forbid extra fields
    }
