from functools import lru_cache

import yaml

from .._models.translator import Translator
from .._settings import settings_manager
from .._types.catalog import Catalog
from .._types.i18n_scope import I18nScope
from .._types.language import Language


@lru_cache(maxsize=None)
def _get_catalog() -> Catalog:
    """Get the translation catalog from settings.

    Returns:
        Translation catalog loaded from file or settings.
    """
    settings = settings_manager.settings

    if settings.catalog_file is not None:
        with open(settings.catalog_file, encoding="utf-8") as f:
            catalog: Catalog = yaml.safe_load(f)
            return catalog
    else:
        return settings.catalog


@lru_cache(maxsize=None)
def get_translator(language: Language, scope: I18nScope) -> Translator:
    """Get a translator for the specified language and scope.

    This function is cached to avoid creating multiple translator instances
    for the same language and scope combination.

    Args:
        language: Target language for translation.
        scope: Scope for translation keys (e.g., "kiarina.app.greeting").

    Returns:
        Translator instance configured for the specified language and scope.

    Example:
        >>> t = get_translator("ja", "app.greeting")
        >>> t("hello", name="World")
        'こんにちは、World!'
    """
    settings = settings_manager.settings
    catalog = _get_catalog()
    return Translator(
        catalog=catalog,
        language=language,
        scope=scope,
        fallback_language=settings.default_language,
    )
