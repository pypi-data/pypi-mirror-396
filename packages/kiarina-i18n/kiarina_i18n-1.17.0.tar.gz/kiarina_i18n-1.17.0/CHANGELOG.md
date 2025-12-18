# Changelog

All notable changes to kiarina-i18n will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.17.0] - 2025-12-15

### Added
- `I18n` base class for type-safe translation definitions with Pydantic validation
- `get_i18n()` helper function to get translated instances with full type safety
- Class-based API for better IDE support and auto-completion
- Immutable translation instances (frozen=True) to prevent accidental modifications
- Self-documenting translation keys using class field definitions
- Automatic fallback to default values when translations are missing

### Changed
- Reorganized test files by target module (_helpers/, _models/)
- Converted class-based tests to function-based tests
- Added pytest fixtures for cache management in tests

## [1.16.0] - 2025-12-15

### Added
- Initial release of kiarina-i18n package
- `Translator` class for translation with fallback support
- `get_translator()` function with caching
- Template variable substitution using Python's string.Template
- Configuration management using pydantic-settings-manager
- Support for loading catalog from YAML file
- Type definitions for Language, I18nScope, I18nKey, and Catalog
