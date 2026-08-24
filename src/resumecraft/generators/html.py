"""Standalone HTML resume generator (also the base for the PDF generator)."""

from __future__ import annotations

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape
from markupsafe import Markup

from resumecraft.exceptions import GenerationError, ThemeError
from resumecraft.generators.base import BaseGenerator
from resumecraft.utils import get_themes_dir

logger = logging.getLogger("resumecraft")


class HTMLGenerator(BaseGenerator):
    """Renders a resume to a single, self-contained HTML file (CSS inlined)."""

    def _theme_dir(self) -> Path:
        theme_dir = get_themes_dir() / self.theme_name
        if not theme_dir.is_dir():
            raise ThemeError(f"Theme directory not found: {theme_dir}")
        return theme_dir

    def render_html(self) -> str:
        """Render the resume to an HTML string, without writing any file."""
        theme_dir = self._theme_dir()
        env = Environment(
            loader=FileSystemLoader(str(theme_dir)),
            autoescape=select_autoescape(["html", "j2"]),
        )

        css_context = {"accent_color": self.accent_color, "font_family": self.font_family}
        try:
            css_template = env.get_template("style.css")
            inline_css = css_template.render(**css_context)
        except TemplateNotFound as e:
            raise ThemeError(f"Theme {self.theme_name!r} is missing style.css") from e

        html_context = {
            "resume": self.data,
            "labels": self.labels,
            "lang": self.lang,
            "present_label": self.present_label(),
            # inline_css is our own rendered CSS, not user input — wrap it as
            # Markup so the (autoescape-on) HTML template doesn't re-escape
            # its quotes. Unescaped, `content: "–";` becomes the invalid
            # `content: &#34;–&#34;;` inside <style>, silently breaking any
            # CSS rule that uses quoted content (e.g. ::before markers).
            "inline_css": Markup(inline_css),
        }
        try:
            html_template = env.get_template("template.html.j2")
            return html_template.render(**html_context)
        except TemplateNotFound as e:
            raise ThemeError(f"Theme {self.theme_name!r} is missing template.html.j2") from e

    def _generate(self, output_path: Path) -> Path:
        try:
            html = self.render_html()
        except ThemeError:
            raise
        except Exception as e:  # jinja2.TemplateError and friends
            raise GenerationError(f"Failed to render HTML resume: {e}") from e

        output_path.write_text(html, encoding="utf-8")
        logger.info("HTML saved: %s", output_path)
        return output_path
