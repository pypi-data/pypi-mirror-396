"""
PromptSentry - AI Prompt Security Scanner

A pre-commit hook and CLI tool for detecting vulnerabilities in AI prompts.
Uses OWASP LLM Top 10 rules and Qwen 2.5 1.5B for intelligent analysis.
"""

__version__ = "0.2.0"
__author__ = "Shaik Anas"

from promptsentry.core.analyzer import PromptAnalyzer
from promptsentry.core.detector import PromptDetector
from promptsentry.core.patterns import PatternMatcher

__all__ = [
    "__version__",
    "PromptDetector",
    "PatternMatcher",
    "PromptAnalyzer",
]
