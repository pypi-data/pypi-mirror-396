"""Mixins for Class-Based Views."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from django.http import HttpRequest, HttpResponse

from django_docxtpl.response import DocxTemplateResponse
from django_docxtpl.utils import OutputFormat


class DocxTemplateResponseMixin:
    """Mixin for views that render DOCX templates.

    This mixin provides functionality to render DOCX templates and serve them
    as documents in various formats (DOCX, PDF, ODT, etc.).

    Attributes:
        template_name: Path to the DOCX template file.
        filename: Output filename without extension.
        output_format: Desired output format (docx, pdf, odt, html, txt).
        as_attachment: Whether to serve as attachment or inline.
        update_fields: Whether to update TOC, charts, and other fields.

    Example:
        class InvoiceView(DocxTemplateResponseMixin, View):
            template_name = "invoices/template.docx"
            filename = "invoice"
            output_format = "pdf"

            def get_context_data(self):
                return {
                    "customer": "John Doe",
                    "items": [...],
                    "total": 100,
                }

            def get(self, request):
                return self.render_to_response()
    """

    template_name: str | Path | None = None
    filename: str = "document"
    output_format: OutputFormat = "docx"
    as_attachment: bool = True
    update_fields: bool = False
    request: HttpRequest  # Type hint for the request attribute from View

    def get_template_name(self) -> str | Path:
        """Return the template name to use for rendering.

        Override this method to dynamically determine the template.

        Returns:
            Path to the template file.

        Raises:
            ValueError: If template_name is not set.
        """
        if self.template_name is None:
            raise ValueError(
                f"{self.__class__.__name__} requires either a definition of "
                "'template_name' or an implementation of 'get_template_name()'"
            )
        return self.template_name

    def get_filename(self) -> str:
        """Return the filename for the generated document.

        Override this method to dynamically determine the filename.

        Returns:
            The filename without extension.
        """
        return self.filename

    def get_output_format(self) -> OutputFormat:
        """Return the output format for the document.

        Override this method to dynamically determine the format.

        Returns:
            The output format string.
        """
        return self.output_format

    def get_update_fields(self) -> bool:
        """Return whether to update fields (TOC, charts, etc.) in the document.

        Override this method to dynamically determine if fields should be updated.
        When True, LibreOffice will process the document to update:
        - Table of Contents (TOC)
        - Charts and graphs
        - Cross-references
        - Page numbers
        - Other calculated fields

        Note: This requires LibreOffice even for DOCX output format.

        Returns:
            True if fields should be updated, False otherwise.
        """
        return self.update_fields

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Return the context dictionary for template rendering.

        Override this method to provide context variables.

        Args:
            **kwargs: Additional context variables.

        Returns:
            Dictionary of context variables.
        """
        return kwargs

    def render_to_response(self, context: dict[str, Any] | None = None) -> HttpResponse:
        """Render the template and return an HTTP response.

        Args:
            context: Optional context dictionary. If not provided,
                    get_context_data() is called.

        Returns:
            DocxTemplateResponse with the rendered document.
        """
        if context is None:
            context = self.get_context_data()

        return DocxTemplateResponse(
            request=self.request,
            template=self.get_template_name(),
            context=context,
            filename=self.get_filename(),
            output_format=self.get_output_format(),
            as_attachment=self.as_attachment,
            update_fields=self.get_update_fields(),
        )
