"""Section labels for supported languages.

Centralized here so HTML, PDF, and DOCX generators always agree on wording
instead of each keeping its own copy (which is how these things drift out
of sync over time).
"""

from __future__ import annotations

from typing import Literal

Lang = Literal["ru", "en"]

SUPPORTED_LANGUAGES: tuple[Lang, ...] = ("ru", "en")

_LABELS: dict[str, dict[str, str]] = {
    "ru": {
        "summary": "Обо мне",
        "experience": "Опыт работы",
        "education": "Образование",
        "skills": "Навыки",
        "projects": "Проекты",
        "languages": "Языки",
        "certifications": "Сертификаты",
        "additional": "Дополнительная информация",
        "present": "настоящее время",
        "contacts": "Контакты",
        "salary": "Зарплата",
    },
    "en": {
        "summary": "About",
        "experience": "Experience",
        "education": "Education",
        "skills": "Skills",
        "projects": "Projects",
        "languages": "Languages",
        "certifications": "Certifications",
        "additional": "Additional Information",
        "present": "Present",
        "contacts": "Contacts",
        "salary": "Salary",
    },
}


def get_labels(lang: str) -> dict[str, str]:
    """Return the label dict for a language, defaulting to English if unknown."""
    return _LABELS.get(lang, _LABELS["en"])
