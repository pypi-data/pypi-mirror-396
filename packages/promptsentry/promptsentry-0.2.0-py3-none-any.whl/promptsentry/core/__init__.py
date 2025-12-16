"""Core pipeline components for PromptSentry."""

from promptsentry.core.analyzer import AnalysisResult, PromptAnalyzer
from promptsentry.core.detector import DetectedPrompt, PromptDetector
from promptsentry.core.patterns import PatternMatch, PatternMatcher
from promptsentry.core.prompt_extractor import (
    ExtractionContext,
    ExtractedString,
    PromptExtractor,
    extract_prompts_from_content,
    extract_prompts_from_file,
)
from promptsentry.core.rules_loader import RulesLoader

# Keep for backward compatibility but deprecated
try:
    from promptsentry.core.vectordb import SimilarMatch, VectorDatabase
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
    # New AST-based extractor
    "PromptExtractor",
    "ExtractedString",
    "ExtractionContext",
    "extract_prompts_from_file",
    "extract_prompts_from_content",
]
