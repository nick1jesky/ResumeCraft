"""Utility functions for ResumeCraft."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any


def setup_logging(debug: bool = False) -> logging.Logger:
    """Configure logging. Uses Rich if available, falls back to plain logging."""
    level = logging.DEBUG if debug else logging.INFO
    try:
        from rich.console import Console
        from rich.logging import RichHandler

        logging.basicConfig(
            level=level,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=Console(stderr=True), rich_tracebacks=True)],
            force=True,
        )
    except ImportError:  # pragma: no cover - fallback path
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)-8s %(message)s",
            force=True,
        )
    return logging.getLogger("resumecraft")


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists, creating parents as needed."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def sanitize_filename(name: str) -> str:
    """Create a safe, lowercase, hyphenated filename from an arbitrary string."""
    safe = re.sub(r"[^\w\s-]", "", name, flags=re.UNICODE).strip()
    safe = re.sub(r"[-\s]+", "-", safe)
    return safe.lower() or "resume"


def load_data_file(path: Path) -> dict[str, Any]:
    """Load a raw dict from a JSON or YAML file (no schema validation)."""
    from resumecraft.exceptions import ValidationError

    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")

    if suffix == ".json":
        import json

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in {path}: {e}") from e

    if suffix in (".yaml", ".yml"):
        import yaml

        try:
            return yaml.safe_load(text)
        except yaml.YAMLError as e:
            raise ValidationError(f"Invalid YAML in {path}: {e}") from e

    raise ValidationError(f"Unsupported file format: {suffix}. Use .json, .yaml, or .yml")


def get_themes_dir() -> Path:
    """Return the directory containing built-in themes."""
    return Path(__file__).parent / "themes"


def list_available_themes() -> list[str]:
    """Return the names of built-in themes that have both a template and stylesheet."""
    themes_dir = get_themes_dir()
    if not themes_dir.is_dir():
        return []
    names = []
    for child in sorted(themes_dir.iterdir()):
        if child.is_dir() and (child / "template.html.j2").exists() and (child / "style.css").exists():
            names.append(child.name)
    return names


_HEX_RE = re.compile(r"^#?([0-9A-Fa-f]{6})$")


def normalize_hex_color(value: str, *, fallback: str = "2B6CB0") -> str:
    """Validate/normalize a hex color string to 6 uppercase hex digits, no '#'."""
    match = _HEX_RE.match(value.strip())
    if not match:
        from resumecraft.exceptions import ConfigError

        raise ConfigError(
            f"Invalid color {value!r}: expected a hex color like '#2B6CB0' or '2B6CB0'"
        )
    return match.group(1).upper()


def rgb_tuple(hex_color: str) -> tuple[int, int, int]:
    """Convert a normalized 6-digit hex string into an (r, g, b) tuple."""
    hex_color = normalize_hex_color(hex_color)
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]
