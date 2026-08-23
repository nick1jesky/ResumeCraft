"""Configuration and settings for ResumeCraft.

Settings are resolved in increasing order of priority:

    built-in defaults  <  config file (resumecraft.toml)  <  environment
    variables (RESUMECRAFT_*)  <  explicit CLI flags

Call :func:`resolve_config` from the CLI (or, later, from an API layer) to
get a single, fully-merged :class:`Config` instance.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Literal

from resumecraft.exceptions import ConfigError
from resumecraft.utils import normalize_hex_color

Theme = Literal[
    "clarity",
    "midnight",
    "accent",
    "editorial",
    "slate",
    "compact",
    "modern",
    "classic",
    "minimal",
    "executive",
    "black-green",
]
OutputFormat = Literal["html", "pdf", "docx", "all"]
Language = Literal["ru", "en"]
PDFBackend = Literal["weasyprint", "pdfkit"]

_ENV_PREFIX = "RESUMECRAFT_"

# Search locations for an implicit config file, in priority order (first match wins).
_DEFAULT_CONFIG_LOCATIONS: tuple[Path, ...] = (
    Path("./resumecraft.toml"),
    Path.home() / ".config" / "resumecraft" / "config.toml",
)


@dataclass(frozen=True)
class Config:
    """Fully-resolved application configuration."""

    output_dir: Path = field(default_factory=lambda: Path("./output"))
    theme: Theme = "clarity"
    format: OutputFormat = "all"
    language: Language = "ru"
    pdf_backend: PDFBackend = "weasyprint"
    wkhtmltopdf_path: str | None = None
    accent_color: str = "2B6CB0"
    font_family: str = "Calibri, 'Segoe UI', Arial, sans-serif"
    debug: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "output_dir", Path(self.output_dir))
        object.__setattr__(self, "accent_color", normalize_hex_color(self.accent_color))

    def merged_with(self, **overrides: Any) -> Config:
        """Return a new Config with only the given, non-None fields overridden."""
        clean = {k: v for k, v in overrides.items() if v is not None}
        if not clean:
            return self
        return replace(self, **clean)


def _load_toml(path: Path) -> dict[str, Any]:
    try:
        import tomllib
    except ModuleNotFoundError as e:  # pragma: no cover - Python < 3.11
        raise ConfigError(
            "Reading .toml config files requires Python 3.11+ (tomllib), "
            "or install the 'tomli' backport."
        ) from e

    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"Invalid TOML in {path}: {e}") from e

    # Allow either a flat file or a [resumecraft] table.
    if "resumecraft" in data and isinstance(data["resumecraft"], dict):
        return data["resumecraft"]
    return data


def find_default_config_file() -> Path | None:
    """Return the first implicit config file that exists, if any."""
    for candidate in _DEFAULT_CONFIG_LOCATIONS:
        if candidate.is_file():
            return candidate
    return None


def load_config_file(path: Path | None) -> dict[str, Any]:
    """Load settings from an explicit or auto-discovered config file.

    Returns an empty dict if no config file was given and none was found —
    a missing config file is not an error, since all settings have defaults.
    """
    if path is None:
        path = find_default_config_file()
        if path is None:
            return {}
    elif not path.is_file():
        raise ConfigError(f"Config file not found: {path}")

    if path.suffix.lower() != ".toml":
        raise ConfigError(f"Unsupported config file format: {path.suffix} (expected .toml)")

    return _load_toml(path)


def load_env_overrides() -> dict[str, Any]:
    """Read RESUMECRAFT_* environment variables into a settings dict."""
    env = os.environ
    overrides: dict[str, Any] = {}

    def _get(name: str) -> str | None:
        return env.get(_ENV_PREFIX + name)

    if v := _get("OUTPUT"):
        overrides["output_dir"] = v
    if v := _get("THEME"):
        overrides["theme"] = v
    if v := _get("FORMAT"):
        overrides["format"] = v
    if v := _get("LANG"):
        overrides["language"] = v
    if v := _get("PDF_BACKEND"):
        overrides["pdf_backend"] = v
    if v := _get("WKHTMLTOPDF_PATH"):
        overrides["wkhtmltopdf_path"] = v
    if v := _get("ACCENT_COLOR"):
        overrides["accent_color"] = v
    if v := _get("FONT_FAMILY"):
        overrides["font_family"] = v
    if v := _get("DEBUG"):
        overrides["debug"] = v.strip().lower() in ("1", "true", "yes", "on")

    return overrides


def resolve_config(
    *,
    config_path: Path | None = None,
    cli_overrides: dict[str, Any] | None = None,
) -> Config:
    """Build the final Config by layering file, env, and CLI settings over defaults.

    ``cli_overrides`` should only contain keys the user *explicitly* passed
    on the command line (i.e. CLI options should default to ``None``, not to
    a hardcoded value, so we can tell "not given" apart from "given, and
    happens to match the default").
    """
    settings: dict[str, Any] = {}
    settings.update(load_config_file(config_path))
    settings.update(load_env_overrides())
    settings.update({k: v for k, v in (cli_overrides or {}).items() if v is not None})

    try:
        return Config(**settings)
    except TypeError as e:
        raise ConfigError(f"Invalid configuration option: {e}") from e
