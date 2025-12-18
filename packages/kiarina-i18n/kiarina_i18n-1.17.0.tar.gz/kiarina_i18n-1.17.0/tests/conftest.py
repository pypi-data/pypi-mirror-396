import pytest


@pytest.fixture
def sample_catalog():
    """Sample translation catalog for testing."""
    return {
        "en": {
            "app.greeting": {
                "hello": "Hello, $name!",
                "goodbye": "Goodbye!",
            },
            "app.error": {
                "not_found": "Not found",
            },
        },
        "ja": {
            "app.greeting": {
                "hello": "こんにちは、$name!",
                "goodbye": "さようなら!",
            },
            "app.error": {
                "not_found": "見つかりません",
            },
        },
    }
