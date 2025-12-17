"""Tests for django_docxtpl.mixins module."""

from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory
from django.views import View

from django_docxtpl.mixins import DocxTemplateResponseMixin


@pytest.fixture
def request_factory():
    """Django request factory."""
    return RequestFactory()


@pytest.fixture
def get_request(request_factory):
    """A simple GET request."""
    return request_factory.get("/")


class TestDocxTemplateResponseMixin:
    """Tests for DocxTemplateResponseMixin."""

    def test_get_template_name(self, simple_docx_template):
        """Test get_template_name returns template_name attribute."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = simple_docx_template

        view = TestView()
        assert view.get_template_name() == simple_docx_template

    def test_get_template_name_not_set(self):
        """Test get_template_name raises error when not set."""

        class TestView(DocxTemplateResponseMixin, View):
            pass

        view = TestView()

        with pytest.raises(ValueError, match="requires either a definition"):
            view.get_template_name()

    def test_get_filename(self):
        """Test get_filename returns filename attribute."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = "test.docx"
            filename = "my_document"

        view = TestView()
        assert view.get_filename() == "my_document"

    def test_get_filename_default(self):
        """Test get_filename default value."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = "test.docx"

        view = TestView()
        assert view.get_filename() == "document"

    def test_get_output_format(self):
        """Test get_output_format returns output_format attribute."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = "test.docx"
            output_format = "pdf"

        view = TestView()
        assert view.get_output_format() == "pdf"

    def test_get_output_format_default(self):
        """Test get_output_format default value."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = "test.docx"

        view = TestView()
        assert view.get_output_format() == "docx"

    def test_get_context_data(self):
        """Test get_context_data returns kwargs."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = "test.docx"

        view = TestView()
        context = view.get_context_data(foo="bar", num=42)

        assert context == {"foo": "bar", "num": 42}

    def test_get_context_data_override(self):
        """Test get_context_data can be overridden."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = "test.docx"

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context["custom"] = "value"
                return context

        view = TestView()
        context = view.get_context_data(foo="bar")

        assert context == {"foo": "bar", "custom": "value"}

    def test_render_to_response(
        self, get_request, simple_docx_template, sample_context
    ):
        """Test render_to_response creates DocxTemplateResponse."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = simple_docx_template
            filename = "test_doc"

        view = TestView()
        view.request = get_request

        response = view.render_to_response(sample_context)

        assert response.status_code == 200
        assert 'filename="test_doc.docx"' in response["Content-Disposition"]

    def test_render_to_response_with_get_context_data(
        self, get_request, simple_docx_template
    ):
        """Test render_to_response uses get_context_data when context is None."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = simple_docx_template

            def get_context_data(self, **kwargs):
                return {"name": "FromMethod", "title": "Title"}

        view = TestView()
        view.request = get_request

        response = view.render_to_response()

        assert response.status_code == 200

    def test_render_to_response_pdf(self, get_request, simple_docx_template):
        """Test render_to_response with PDF output format."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = simple_docx_template
            output_format = "pdf"

        view = TestView()
        view.request = get_request

        with patch("django_docxtpl.response.convert_docx") as mock_convert:
            mock_convert.return_value = b"%PDF fake"

            response = view.render_to_response({"name": "Test", "title": "Title"})

            assert response["Content-Type"] == "application/pdf"

    def test_as_attachment_default(self, get_request, simple_docx_template):
        """Test as_attachment is True by default."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = simple_docx_template

        view = TestView()
        view.request = get_request

        response = view.render_to_response({"name": "Test", "title": "Title"})

        assert response["Content-Disposition"].startswith("attachment;")

    def test_as_attachment_false(self, get_request, simple_docx_template):
        """Test as_attachment can be set to False."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = simple_docx_template
            as_attachment = False

        view = TestView()
        view.request = get_request

        response = view.render_to_response({"name": "Test", "title": "Title"})

        assert response["Content-Disposition"].startswith("inline;")


class TestDynamicMethods:
    """Tests for dynamically overriding mixin methods."""

    def test_dynamic_template_name(self, get_request, simple_docx_template):
        """Test dynamically determining template name."""

        class TestView(DocxTemplateResponseMixin, View):
            def get_template_name(self):
                return simple_docx_template

        view = TestView()
        view.request = get_request

        response = view.render_to_response({"name": "Test", "title": "Title"})
        assert response.status_code == 200

    def test_dynamic_filename(self, get_request, simple_docx_template):
        """Test dynamically determining filename."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = simple_docx_template

            def get_filename(self):
                return "dynamic_name"

        view = TestView()
        view.request = get_request

        response = view.render_to_response({"name": "Test", "title": "Title"})
        assert 'filename="dynamic_name.docx"' in response["Content-Disposition"]

    def test_dynamic_output_format(self, get_request, simple_docx_template):
        """Test dynamically determining output format."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = simple_docx_template

            def get_output_format(self):
                return "docx"  # Keep docx to avoid LibreOffice dependency

        view = TestView()
        view.request = get_request

        response = view.render_to_response({"name": "Test", "title": "Title"})
        assert response.status_code == 200


class TestUpdateFieldsMixin:
    """Tests for update_fields functionality in mixin."""

    def test_get_update_fields_default(self, simple_docx_template):
        """Test get_update_fields returns False by default."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = simple_docx_template

        view = TestView()
        assert view.get_update_fields() is False

    def test_get_update_fields_attribute(self, simple_docx_template):
        """Test get_update_fields returns update_fields attribute."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = simple_docx_template
            update_fields = True

        view = TestView()
        assert view.get_update_fields() is True

    def test_get_update_fields_override(self, simple_docx_template):
        """Test get_update_fields can be overridden."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = simple_docx_template

            def get_update_fields(self):
                return True

        view = TestView()
        assert view.get_update_fields() is True

    def test_render_to_response_passes_update_fields(
        self, get_request, simple_docx_template
    ):
        """Test render_to_response passes update_fields to response."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = simple_docx_template
            update_fields = True

        view = TestView()
        view.request = get_request

        with patch("django_docxtpl.mixins.DocxTemplateResponse") as mock_response:
            mock_response.return_value = MagicMock(status_code=200)

            view.render_to_response({"name": "Test", "title": "Title"})

            mock_response.assert_called_once()
            _, kwargs = mock_response.call_args
            assert kwargs.get("update_fields") is True

    def test_dynamic_update_fields(self, get_request, simple_docx_template):
        """Test dynamically determining update_fields."""

        class TestView(DocxTemplateResponseMixin, View):
            template_name = simple_docx_template

            def get_update_fields(self):
                # Only update fields for PDF output
                return self.get_output_format() == "pdf"

        view = TestView()
        view.request = get_request

        # Default output is docx, so update_fields should be False
        assert view.get_update_fields() is False

        # Change output format
        view.output_format = "pdf"
        assert view.get_update_fields() is True
