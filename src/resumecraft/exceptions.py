"""Custom exceptions for ResumeCraft."""

from __future__ import annotations


class ResumeCraftError(Exception):
    """Base exception for all ResumeCraft errors."""


class ValidationError(ResumeCraftError):
    """Raised when resume data fails validation or a data file is malformed."""


class ConfigError(ResumeCraftError):
    """Raised when configuration (file, env, or CLI) is invalid."""


class ThemeError(ResumeCraftError):
    """Raised when a theme-related error occurs (unknown theme, missing asset)."""


class GenerationError(ResumeCraftError):
    """Raised when document generation fails."""


class PDFBackendError(GenerationError):
    """Raised when a PDF backend fails to initialize or render."""
