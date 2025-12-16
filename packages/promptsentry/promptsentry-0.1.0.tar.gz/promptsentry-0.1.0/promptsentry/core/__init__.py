"""Core pipeline components for PromptSentry."""

from promptsentry.core.detector import PromptDetector, DetectedPrompt
from promptsentry.core.patterns import PatternMatcher, PatternMatch
from promptsentry.core.rules_loader import RulesLoader
from promptsentry.core.analyzer import PromptAnalyzer, AnalysisResult

# Keep for backward compatibility but deprecated
try:
    from promptsentry.core.vectordb import VectorDatabase, SimilarMatch
except ImportError:
    VectorDatabase = None
    SimilarMatch = None

__all__ = [
    "PromptDetector",
    "DetectedPrompt",
    "PatternMatcher",
    "PatternMatch",
    "RulesLoader",
    "PromptAnalyzer",
    "AnalysisResult",
]
