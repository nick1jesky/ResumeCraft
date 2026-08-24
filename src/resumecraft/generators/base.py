"""Shared base class for all output generators."""

from __future__ import annotations

from pathlib import Path

from resumecraft.exceptions import ThemeError
from resumecraft.locales import get_labels
from resumecraft.models import ResumeData
from resumecraft.utils import ensure_dir, list_available_themes, normalize_hex_color


class BaseGenerator:
    """Common state/behavior for HTML, PDF, and DOCX generators.

    Kept deliberately free of CLI concerns (argument parsing, console
    printing) so this same class can be driven by a future API layer, a
    test suite, or any other caller — not just ``cli.py``.
    """

    #: Themes each generator subclass knows how to render. HTML/PDF use all
    #: three built-in themes; DOCX renders one consistent style but still
    #: respects accent_color/font_family, so it accepts the same set.
    SUPPORTED_THEMES: tuple[str, ...] = (
        "clarity",
        "midnight",
        "obsidian",
        "accent",
        "editorial",
        "slate",
        "compact",
        "terminal",
        "modern",
        "classic",
        "minimal",
        "executive",
        "black-green",
    )

    def __init__(
        self,
        data: ResumeData,
        *,
        theme_name: str = "clarity",
        lang: str = "ru",
        accent_color: str = "2B6CB0",
        font_family: str = "Calibri, 'Segoe UI', Arial, sans-serif",
    ) -> None:
        if theme_name not in self.SUPPORTED_THEMES:
            available = ", ".join(list_available_themes()) or "(none found)"
            raise ThemeError(
                f"Unknown theme {theme_name!r}. Available themes: {available}"
            )
        self.data = data
        self.theme_name = theme_name
        self.lang = lang
        self.accent_color = normalize_hex_color(accent_color)
        self.font_family = font_family
        self.labels = get_labels(lang)

    def generate(self, output_path: Path) -> Path:
        """Render the resume and write it to ``output_path``. Returns the path."""
        ensure_dir(output_path.parent)
        return self._generate(output_path)

    def _generate(self, output_path: Path) -> Path:  # pragma: no cover - abstract
        raise NotImplementedError

    def present_label(self) -> str:
        return self.labels["present"]
