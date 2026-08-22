"""Core generation service.

This module has no knowledge of argument parsing, console output, or exit
codes — it's the reusable core that both `cli.py` and a future API layer
(e.g. a FastAPI app exposing POST /resumes) call into. Keeping it separate
means adding an API later is a matter of writing a thin HTTP wrapper around
`generate_resume`, not duplicating logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from resumecraft.config import Config
from resumecraft.generators import DOCXGenerator, HTMLGenerator, PDFGenerator
from resumecraft.models import ResumeData
from resumecraft.utils import ensure_dir, sanitize_filename

_GENERATORS = {
    "html": HTMLGenerator,
    "docx": DOCXGenerator,
}


@dataclass
class GeneratedFile:
    format: str
    path: Path


def load_resume(input_path: Path) -> ResumeData:
    """Load and validate a resume from a .json/.yaml/.yml file."""
    suffix = input_path.suffix.lower()
    if suffix == ".json":
        return ResumeData.from_json(str(input_path))
    if suffix in (".yaml", ".yml"):
        return ResumeData.from_yaml(str(input_path))

    from resumecraft.exceptions import ValidationError

    raise ValidationError(f"Input file must be .json, .yaml, or .yml (got {suffix})")


def resolve_formats(requested: str) -> list[str]:
    return ["html", "pdf", "docx"] if requested == "all" else [requested]


def generate_resume(data: ResumeData, config: Config) -> list[GeneratedFile]:
    """Generate one or more resume files for `data` according to `config`.

    Returns the list of files actually written. Raises ResumeCraftError
    subclasses (ThemeError, GenerationError, PDFBackendError, ...) on
    failure — callers (CLI, API, tests) decide how to present that.
    """
    ensure_dir(config.output_dir)
    base_name = sanitize_filename(data.full_name)
    written: list[GeneratedFile] = []

    for fmt in resolve_formats(config.format):
        file_path = config.output_dir / f"{base_name}.{fmt}"

        if fmt == "pdf":
            generator = PDFGenerator(
                data,
                theme_name=config.theme,
                lang=config.language,
                accent_color=config.accent_color,
                font_family=config.font_family,
                backend=config.pdf_backend,
                wkhtmltopdf_path=config.wkhtmltopdf_path,
            )
        else:
            generator_cls = _GENERATORS[fmt]
            generator = generator_cls(
                data,
                theme_name=config.theme,
                lang=config.language,
                accent_color=config.accent_color,
                font_family=config.font_family,
            )

        generator.generate(file_path)
        written.append(GeneratedFile(format=fmt, path=file_path))

    return written
