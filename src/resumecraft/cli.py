"""Command-line interface for ResumeCraft."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from resumecraft import __version__
from resumecraft.config import resolve_config
from resumecraft.exceptions import ResumeCraftError
from resumecraft.service import generate_resume, load_resume
from resumecraft.utils import list_available_themes, setup_logging

try:
    from rich.console import Console

    _console = Console()

    def _print(msg: str) -> None:
        _console.print(msg)

except ImportError:  # pragma: no cover - plain fallback when rich isn't installed
    import re

    _TAG_RE = re.compile(r"\[/?[a-zA-Z ]+\]")

    def _print(msg: str) -> None:
        click.echo(_TAG_RE.sub("", msg))


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="resumecraft")
@click.argument("input_file", required=False, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Директория вывода [default: ./output или config/env]",
)
@click.option(
    "--format", "-f",
    type=click.Choice(["html", "pdf", "docx", "all"], case_sensitive=False),
    default=None,
    help="Выбор формата выходного документа [default: all]",
)
@click.option(
    "--theme", "-t",
    type=click.Choice(
        [
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
        ],
        case_sensitive=False,
    ),
    default=None,
    help="Выбор темы [default: clarity]",
)
@click.option(
    "--lang", "-l",
    type=click.Choice(["ru", "en"], case_sensitive=False),
    default=None,
    help="Выбор языка [default: ru]",
)
@click.option(
    "--accent-color",
    default=None,
    help="Цвет акцентов в hex формате [default: 2B6CB0]",
)
@click.option(
    "--font",
    "font_family",
    default=None,
    help="Шрифт"
)
@click.option(
    "--pdf-backend",
    type=click.Choice(["weasyprint", "pdfkit"], case_sensitive=False),
    default=None,
    help="backend PDF генерации [default: weasyprint]",
)
@click.option(
    "--wkhtmltopdf-path",
    type=click.Path(exists=True),
    default=None,
    help="Путь к wkhtmltopdf (использовать только с --pdf-backend pdfkit)",
)
@click.option(
    "--config", "config_path",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Путь к resumecraft.toml",
)
@click.option("--debug", is_flag=True, default=None, help="Включить debug логирование")
@click.option("--list-themes", is_flag=True, help="Список доступных тем")
def main(
    input_file: Path | None,
    output: Path | None,
    format: str | None,
    theme: str | None,
    lang: str | None,
    accent_color: str | None,
    font_family: str | None,
    pdf_backend: str | None,
    wkhtmltopdf_path: str | None,
    config_path: Path | None,
    debug: bool | None,
    list_themes: bool,
) -> None:
    """ResumeCraft — это генератор профессиональных резюме, который форматирует в ваши вводные данные в красиво оформленные документы в форматах HTML, PDF и DOCX из JSON и YAML файлов."""
    if list_themes:
        for name in list_available_themes():
            _print(f"  • {name}")
        return

    if input_file is None:
        raise click.UsageError("Missing argument 'INPUT_FILE'. See --help.")

    try:
        config = resolve_config(
            config_path=config_path,
            cli_overrides={
                "output_dir": output,
                "format": format.lower() if format else None,
                "theme": theme.lower() if theme else None,
                "language": lang.lower() if lang else None,
                "accent_color": accent_color,
                "font_family": font_family,
                "pdf_backend": pdf_backend.lower() if pdf_backend else None,
                "wkhtmltopdf_path": wkhtmltopdf_path,
                "debug": debug,
            },
        )
    except ResumeCraftError as e:
        _print(f"[bold red]Config error:[/] {e}")
        sys.exit(1)

    logger = setup_logging(config.debug)

    try:
        data = load_resume(input_file)
        _print(f"[bold green]✓[/] Loaded resume for [bold]{data.full_name}[/]")

        written = generate_resume(data, config)

        for item in written:
            _print(f"[bold blue]→[/] {item.path}")

        _print(f"[bold green]🎉 Done! Files saved to {config.output_dir}[/]")

    except ResumeCraftError as e:
        _print(f"[bold red]Error:[/] {e}")
        sys.exit(1)
    except Exception as e:  # noqa: BLE001 - top-level safety net for the CLI
        logger.exception("Unexpected error")
        _print(f"[bold red]Unexpected error:[/] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
