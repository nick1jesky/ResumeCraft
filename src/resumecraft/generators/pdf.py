"""PDF resume generator. Renders HTML first, then converts via a chosen backend."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from resumecraft.exceptions import GenerationError, PDFBackendError
from resumecraft.generators.base import BaseGenerator
from resumecraft.generators.html import HTMLGenerator

logger = logging.getLogger("resumecraft")

_SUPPORTED_BACKENDS = ("weasyprint", "pdfkit")


class PDFGenerator(BaseGenerator):
    """Generates a PDF resume via WeasyPrint (pure Python) or pdfkit (wkhtmltopdf)."""

    def __init__(
        self,
        data,
        *,
        theme_name: str = "modern",
        lang: str = "ru",
        accent_color: str = "2B6CB0",
        font_family: str = "Calibri, 'Segoe UI', Arial, sans-serif",
        backend: str = "weasyprint",
        wkhtmltopdf_path: str | None = None,
    ) -> None:
        super().__init__(
            data,
            theme_name=theme_name,
            lang=lang,
            accent_color=accent_color,
            font_family=font_family,
        )
        if backend not in _SUPPORTED_BACKENDS:
            raise PDFBackendError(
                f"Unknown PDF backend {backend!r}. Supported: {', '.join(_SUPPORTED_BACKENDS)}"
            )
        self.backend = backend
        self.wkhtmltopdf_path = wkhtmltopdf_path
        self._html_generator = HTMLGenerator(
            data,
            theme_name=theme_name,
            lang=lang,
            accent_color=accent_color,
            font_family=font_family,
        )

    def _generate(self, output_path: Path) -> Path:
        html = self._html_generator.render_html()

        if self.backend == "weasyprint":
            self._render_weasyprint(html, output_path)
        else:
            self._render_pdfkit(html, output_path)

        logger.info("PDF saved (%s): %s", self.backend, output_path)
        return output_path

    def _render_weasyprint(self, html: str, output_path: Path) -> None:
        try:
            from weasyprint import HTML
        except ModuleNotFoundError as e:
            raise PDFBackendError(
                "Backend 'weasyprint' is selected but the 'weasyprint' package "
                "is not installed. Install it with: pip install weasyprint "
                "— or pass --pdf-backend pdfkit to use wkhtmltopdf instead."
            ) from e

        try:
            HTML(string=html, base_url=str(Path.cwd())).write_pdf(str(output_path))
        except Exception as e:
            raise GenerationError(f"WeasyPrint failed to render PDF: {e}") from e

    def _render_pdfkit(self, html: str, output_path: Path) -> None:
        try:
            import pdfkit
        except ModuleNotFoundError as e:
            raise PDFBackendError(
                "Backend 'pdfkit' is selected but the 'pdfkit' package is not "
                "installed. Install it with: pip install pdfkit"
            ) from e

        wkhtmltopdf_bin = self.wkhtmltopdf_path or shutil.which("wkhtmltopdf")
        if not wkhtmltopdf_bin:
            raise PDFBackendError(
                "Backend 'pdfkit' needs the wkhtmltopdf binary. It wasn't found "
                "on PATH — pass --wkhtmltopdf-path /path/to/wkhtmltopdf, or set "
                "the WKHTMLTOPDF_PATH environment variable."
            )

        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_bin)
        options = {
            "encoding": "UTF-8",
            "enable-local-file-access": None,
            "quiet": "",
            "page-size": "A4",
            "margin-top": "0mm",
            "margin-bottom": "0mm",
            "margin-left": "0mm",
            "margin-right": "0mm",
            "disable-smart-shrinking": None,
            "print-media-type": None,
        }
        try:
            pdfkit.from_string(html, str(output_path), configuration=config, options=options)
        except OSError as e:
            raise PDFBackendError(
                f"wkhtmltopdf binary at {wkhtmltopdf_bin!r} could not be run: {e}"
            ) from e
        except Exception as e:
            raise GenerationError(f"pdfkit failed to render PDF: {e}") from e
