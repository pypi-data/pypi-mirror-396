"""
Quality module for the autonomous coding system.

Contains:
- qa_agent: QA Agent for quality validation
- gates: Quality gate implementations (Lint, TypeCheck, UnitTests, etc.)
- spec_validator: Pre-coding spec validation
"""

from quality.gates import (
    BrowserAutomationGate,
    LintGate,
    QualityGate,
    StoryValidationGate,
    TypeCheckGate,
    UnitTestGate,
)
from quality.qa_agent import QAAgent
from quality.spec_validator import SpecValidator, run_spec_validator

__all__ = [
    "QualityGate",
    "LintGate",
    "TypeCheckGate",
    "UnitTestGate",
    "BrowserAutomationGate",
    "StoryValidationGate",
    "QAAgent",
    "SpecValidator",
    "run_spec_validator",
]
