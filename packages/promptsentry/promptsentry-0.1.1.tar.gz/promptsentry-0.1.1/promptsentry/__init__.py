"""
PromptSentry - AI Prompt Security Scanner

A pre-commit hook and CLI tool for detecting vulnerabilities in AI prompts.
Uses OWASP LLM Top 10 rules and Qwen 2.5 1.5B for intelligent analysis.
"""

__version__ = "0.1.0"
__author__ = "PromptSentry Team"

from promptsentry.core.detector import PromptDetector
from promptsentry.core.patterns import PatternMatcher
from promptsentry.core.analyzer import PromptAnalyzer

__all__ = [
    "__version__",
    "PromptDetector",
    "PatternMatcher", 
    "PromptAnalyzer",
]
