"""Pydantic models for resume data validation."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

# NOTE: only ever import the *class* `datetime` here, never `import datetime`
# (the bare module import). If both names exist in this module, whichever
# import runs last silently wins, and `datetime.strptime(...)` will then be
# resolved against the *module* (which has no such attribute) instead of the
# class. That was the root cause of a previous "module 'datetime' has no
# attribute 'strptime'" bug.

_DATE_FORMATS = ("%m.%Y", "%Y-%m", "%Y")


def _parse_date(date_str: str) -> date:
    """Parse 'MM.YYYY', 'YYYY-MM' or 'YYYY' into a date object for comparison."""
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {date_str!r}")


class Experience(BaseModel):
    """Work experience entry."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    company: str = Field(..., min_length=1, description="Company or organization name")
    position: str = Field(..., min_length=1, description="Job title")
    location: str = Field(default="", description="City, country or remote")
    start_date: str = Field(
        ...,
        pattern=r"^(\d{2}\.\d{4}|\d{4}-\d{2}|\d{4})$",
        description="Start date: MM.YYYY, YYYY-MM or YYYY",
    )
    end_date: str | None = Field(
        default=None,
        pattern=r"^(\d{2}\.\d{4}|\d{4}-\d{2}|\d{4})$",
        description="End date, or None for present",
    )
    description: list[str] = Field(
        default_factory=list,
        min_length=1,
        description="Bullet points describing responsibilities and achievements",
    )

    @field_validator("description")
    @classmethod
    def _validate_description(cls, v: list[str]) -> list[str]:
        cleaned = [item.strip() for item in v if item.strip()]
        if not cleaned:
            raise ValueError("At least one non-empty description item is required")
        return cleaned

    @model_validator(mode="after")
    def _check_dates(self) -> Self:
        """Ensure end_date is not before start_date."""
        if self.end_date is None:
            return self
        start = _parse_date(self.start_date)
        end = _parse_date(self.end_date)
        if end < start:
            raise ValueError(
                f"end_date ({self.end_date}) cannot be before start_date ({self.start_date})"
            )
        return self

    @property
    def is_current(self) -> bool:
        """Return True if this is the current position."""
        return self.end_date is None

    def duration_text(self, present_label: str = "Present") -> str:
        """Human-readable duration string in the requested language."""
        end = self.end_date or present_label
        return f"{self.start_date} – {end}"


class Education(BaseModel):
    """Education entry."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    institution: str = Field(..., min_length=1, description="University, college or school")
    degree: str = Field(..., min_length=1, description="Degree level (e.g. Bachelor, Master)")
    field: str = Field(default="", description="Field of study")
    start_year: int = Field(..., ge=1900, le=2100, description="Start year")
    end_year: int | None = Field(default=None, ge=1900, le=2100, description="End year or None")
    location: str = Field(default="", description="City, country")
    gpa: str | None = Field(default=None, description="GPA or grade")

    @model_validator(mode="after")
    def _check_years(self) -> Self:
        if self.end_year is not None and self.end_year < self.start_year:
            raise ValueError("end_year cannot be before start_year")
        return self

    def duration_text(self, present_label: str = "Present") -> str:
        """Human-readable duration string in the requested language."""
        end = self.end_year if self.end_year is not None else present_label
        return f"{self.start_year} – {end}"


class SkillCategory(BaseModel):
    """Group of related skills."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    category: str = Field(..., min_length=1, description="Category name")
    items: list[str] = Field(
        ...,
        min_length=1,
        description="List of skills in this category",
    )

    @field_validator("items")
    @classmethod
    def _validate_items(cls, v: list[str]) -> list[str]:
        cleaned = [item.strip() for item in v if item.strip()]
        if not cleaned:
            raise ValueError("At least one non-empty skill is required")
        return cleaned


class Project(BaseModel):
    """Personal or professional project."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    name: str = Field(..., min_length=1)
    description: str = Field(default="")
    url: str | None = Field(default=None)
    technologies: list[str] = Field(default_factory=list)


class LanguageSkill(BaseModel):
    """A spoken/written language with a proficiency level."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    language: str = Field(..., min_length=1)
    level: str = Field(default="", description="e.g. Native, Fluent, B2, Intermediate")


class ResumeData(BaseModel):
    """Complete resume data model."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    full_name: str = Field(..., min_length=1, description="Full name")
    title: str = Field(..., min_length=1, description="Professional title / headline")
    location: str = Field(default="", description="City, country")
    phone: str = Field(..., min_length=5, description="Phone number")
    email: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Email address",
    )
    salary: str | None = Field(default=None, description="Desired or current salary")
    linkedin: str | None = Field(default=None, description="LinkedIn URL or handle")
    github: str | None = Field(default=None, description="GitHub URL or handle")
    website: str | None = Field(default=None, description="Personal website URL")
    summary: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Professional summary / about me",
    )
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: list[SkillCategory] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    languages: list[LanguageSkill] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    additional: str | None = Field(default=None, description="Additional free-form information")

    @field_validator("phone")
    @classmethod
    def _validate_phone(cls, v: str) -> str:
        digits = re.sub(r"\D", "", v)
        if len(digits) < 7:
            raise ValueError("Phone number must contain at least 7 digits")
        return v.strip()

    @field_validator("linkedin", "github", "website")
    @classmethod
    def _normalize_url(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if not v:
            return None
        # A bare handle like "johndoe" (no dots, no slashes) is left as-is;
        # anything else is assumed to be a URL and gets a scheme if missing.
        if "://" not in v and "/" not in v and "." not in v:
            return v
        if not v.startswith(("http://", "https://")):
            v = "https://" + v
        return v

    @model_validator(mode="after")
    def _check_content(self) -> Self:
        """Ensure the resume has at least some content to render."""
        if not any([self.experience, self.education, self.projects, self.skills]):
            raise ValueError(
                "Resume must contain at least one of: experience, education, projects, or skills"
            )
        return self

    @classmethod
    def from_json(cls, path: str) -> Self:
        """Load resume data from a JSON file."""
        import json
        from pathlib import Path

        raw = Path(path).read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            from resumecraft.exceptions import ValidationError

            raise ValidationError(f"Invalid JSON in {path}: {e}") from e
        return cls._validate_dict(data, path)

    @classmethod
    def from_yaml(cls, path: str) -> Self:
        """Load resume data from a YAML file."""
        import yaml
        from pathlib import Path

        raw = Path(path).read_text(encoding="utf-8")
        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError as e:
            from resumecraft.exceptions import ValidationError

            raise ValidationError(f"Invalid YAML in {path}: {e}") from e
        return cls._validate_dict(data, path)

    @classmethod
    def _validate_dict(cls, data: Any, source: str) -> Self:
        from pydantic import ValidationError as PydanticValidationError

        from resumecraft.exceptions import ValidationError

        if not isinstance(data, dict):
            raise ValidationError(
                f"{source}: expected a JSON/YAML object at the top level, got {type(data).__name__}"
            )
        try:
            return cls.model_validate(data)
        except PydanticValidationError as e:
            raise ValidationError(f"{source}: {e}") from e

    def to_json(self, path: str | None = None) -> str:
        """Export resume data to a JSON string, optionally writing it to a file."""
        from pathlib import Path

        json_str = self.model_dump_json(indent=2, exclude_none=True)
        if path:
            Path(path).write_text(json_str, encoding="utf-8")
        return json_str
