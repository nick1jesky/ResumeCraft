"""ResumeCraft — это генератор профессиональных резюме, который форматирует в ваши вводные данные в красиво оформленные документы в форматах HTML, PDF и DOCX."""

from resumecraft.models import (
    Education,
    Experience,
    LanguageSkill,
    Project,
    ResumeData,
    SkillCategory,
)
from resumecraft.generators.html import HTMLGenerator
from resumecraft.generators.pdf import PDFGenerator
from resumecraft.generators.docx import DOCXGenerator
from resumecraft.config import Config, resolve_config
from resumecraft.service import generate_resume, load_resume

__version__ = "0.0.1 PreRelease"
__all__ = [
    "ResumeData",
    "Experience",
    "Education",
    "SkillCategory",
    "Project",
    "LanguageSkill",
    "HTMLGenerator",
    "PDFGenerator",
    "DOCXGenerator",
    "Config",
    "resolve_config",
    "generate_resume",
    "load_resume",
]
