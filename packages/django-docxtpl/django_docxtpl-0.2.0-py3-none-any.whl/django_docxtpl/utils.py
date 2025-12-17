"""Utility functions for django-docxtpl."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Literal

from django.conf import settings

# Supported output formats
OutputFormat = Literal["docx", "pdf", "odt", "html", "txt"]

# MIME types for each format
CONTENT_TYPES: dict[str, str] = {
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pdf": "application/pdf",
    "odt": "application/vnd.oasis.opendocument.text",
    "html": "text/html",
    "txt": "text/plain",
}

# File extensions for each format
EXTENSIONS: dict[str, str] = {
    "docx": ".docx",
    "pdf": ".pdf",
    "odt": ".odt",
    "html": ".html",
    "txt": ".txt",
}

# Default paths to search for LibreOffice
LIBREOFFICE_PATHS = [
    # macOS
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    # Linux
    "/usr/bin/soffice",
    "/usr/bin/libreoffice",
    "/usr/local/bin/soffice",
    # Windows (common paths)
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
]


def get_content_type(output_format: OutputFormat) -> str:
    """Get the MIME content type for a given output format.

    Args:
        output_format: The output format (docx, pdf, odt, html, txt).

    Returns:
        The MIME content type string.

    Raises:
        ValueError: If the format is not supported.
    """
    if output_format not in CONTENT_TYPES:
        raise ValueError(
            f"Unsupported format: {output_format}. "
            f"Supported formats: {', '.join(CONTENT_TYPES.keys())}"
        )
    return CONTENT_TYPES[output_format]


def get_extension(output_format: OutputFormat) -> str:
    """Get the file extension for a given output format.

    Args:
        output_format: The output format (docx, pdf, odt, html, txt).

    Returns:
        The file extension including the dot (e.g., '.pdf').

    Raises:
        ValueError: If the format is not supported.
    """
    if output_format not in EXTENSIONS:
        raise ValueError(
            f"Unsupported format: {output_format}. "
            f"Supported formats: {', '.join(EXTENSIONS.keys())}"
        )
    return EXTENSIONS[output_format]


def get_filename_with_extension(filename: str, output_format: OutputFormat) -> str:
    """Add the correct extension to a filename based on the output format.

    If the filename already has the correct extension, it's returned as-is.
    If it has a different extension, the correct one is appended.

    Args:
        filename: The base filename (with or without extension).
        output_format: The desired output format.

    Returns:
        The filename with the correct extension.
    """
    extension = get_extension(output_format)
    if filename.lower().endswith(extension):
        return filename
    # Remove any existing extension from supported formats
    for ext in EXTENSIONS.values():
        if filename.lower().endswith(ext):
            filename = filename[: -len(ext)]
            break
    return f"{filename}{extension}"


def find_libreoffice() -> Path | None:
    """Find the LibreOffice executable.

    Searches in the following order:
    1. Django setting DOCXTPL_LIBREOFFICE_PATH
    2. System PATH (using shutil.which)
    3. Common installation locations

    Returns:
        Path to the LibreOffice executable, or None if not found.
    """
    # Check Django settings first
    custom_path = getattr(settings, "DOCXTPL_LIBREOFFICE_PATH", None)
    if custom_path:
        path = Path(custom_path)
        if path.exists() and path.is_file():
            return path

    # Check system PATH
    for cmd in ["soffice", "libreoffice"]:
        found = shutil.which(cmd)
        if found:
            return Path(found)

    # Check common installation paths
    for path_str in LIBREOFFICE_PATHS:
        path = Path(path_str)
        if path.exists() and path.is_file():
            return path

    return None


def get_template_dir() -> Path | None:
    """Get the configured template directory for DOCX templates.

    Returns:
        Path to the template directory, or None if not configured.
    """
    template_dir = getattr(settings, "DOCXTPL_TEMPLATE_DIR", None)
    if template_dir:
        return Path(template_dir)
    return None


def render_to_file(
    template: str | Path,
    context: dict[str, Any],
    output_dir: str | Path,
    filename: str,
    output_format: OutputFormat = "docx",
    *,
    update_fields: bool = False,
) -> Path:
    """Render a DOCX template and save to a file.

    This is useful for background tasks (Celery, Huey, RQ) where you need
    to generate a document and save it to disk without an HTTP response.

    Args:
        template: Path to the DOCX template file (absolute or relative to
                 DOCXTPL_TEMPLATE_DIR).
        context: Dictionary of context variables for template rendering.
        output_dir: Directory where the output file will be saved.
        filename: Output filename without extension.
        output_format: Desired output format (docx, pdf, odt, html, txt).
        update_fields: If True, update TOC, charts, and other dynamic fields.

    Returns:
        Absolute path to the generated file.

    Raises:
        FileNotFoundError: If the template file doesn't exist.
        LibreOfficeNotFoundError: If LibreOffice is needed but not found.
        ConversionError: If the conversion fails.

    Example:
        from django_docxtpl.utils import render_to_file

        output_path = render_to_file(
            template="reports/monthly.docx",
            context={"month": "December", "data": report_data},
            output_dir="/tmp/reports",
            filename="monthly_report",
            output_format="pdf",
            update_fields=True,
        )
    """
    from io import BytesIO

    from docxtpl import DocxTemplate  # type: ignore[import-untyped]

    from django_docxtpl.converters import convert_docx, update_fields_in_docx

    # Resolve template path
    template_path = Path(template)
    if not template_path.is_absolute():
        template_dir = get_template_dir()
        if template_dir:
            full_path = template_dir / template_path
            if full_path.exists():
                template_path = full_path
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template}")

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    # Load and render the template
    doc = DocxTemplate(template_path)
    doc.render(context)

    # Save to BytesIO
    docx_buffer = BytesIO()
    doc.save(docx_buffer)
    docx_buffer.seek(0)

    # Process the document
    if output_format == "docx":
        if update_fields:
            content = update_fields_in_docx(docx_buffer)
        else:
            content = docx_buffer.getvalue()
    else:
        content = convert_docx(docx_buffer, output_format, update_fields=update_fields)

    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Build full filename with extension
    full_filename = get_filename_with_extension(filename, output_format)
    file_path = output_path / full_filename

    # Write to file
    file_path.write_bytes(content)

    return file_path.resolve()
