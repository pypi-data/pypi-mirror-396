# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2024-12-14

### Added
- `update_fields` parameter to update TOC, charts, cross-references, and other dynamic fields using LibreOffice
- `update_fields_in_docx()` function to process DOCX files and update all fields
- `render_to_file()` utility function for generating documents to disk (useful for background tasks with Celery, Huey, RQ)
- `get_update_fields()` method in mixins for dynamic control
- LibreOffice installation instructions for headless servers (Ubuntu, Alpine, RHEL)
- Performance considerations and task queue examples in documentation

### Changed
- `convert_docx()` now accepts `update_fields` parameter
- `DocxTemplateResponse` now accepts `update_fields` parameter
- `DocxTemplateView` and `DocxTemplateDetailView` now support `update_fields` attribute

## [0.1.0] - 2024-12-14

### Added
- Initial release
- `DocxTemplateResponse` for function-based views
- `DocxTemplateView` for class-based views
- `DocxTemplateDetailView` for model-based document generation
- `DocxTemplateResponseMixin` for custom view classes
- Multi-format output support: DOCX, PDF, ODT, HTML, TXT
- Automatic LibreOffice detection
- Automatic file extension based on output format
- Django settings: `DOCXTPL_TEMPLATE_DIR`, `DOCXTPL_LIBREOFFICE_PATH`
- Full type hints support
- Comprehensive test suite

### Dependencies
- Python >= 3.10
- Django >= 4.2
- docxtpl >= 0.16

[Unreleased]: https://github.com/ctrl-alt-d/django-docxtpl/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/ctrl-alt-d/django-docxtpl/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ctrl-alt-d/django-docxtpl/releases/tag/v0.1.0
