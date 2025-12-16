"""
Stage 1: Prompt Detector

Quickly identifies AI prompts in source code using heuristics and pattern matching.
This is the first stage of the PromptSentry pipeline - a fast filter to identify
files that need deeper analysis.

Detection Modes:
- AST Mode (default): Uses Python AST for accurate extraction with context scoring
- Regex Mode (fallback): Uses regex patterns for speed or non-parseable content
"""

import re
from pathlib import Path
from typing import Optional

from promptsentry.core.prompt_extractor import PromptExtractor, ExtractedString
from promptsentry.models.detection import DetectedPrompt, DetectionSignals, PromptLocation


class PromptDetector:
    """
    Detects AI prompts in source code using multi-signal heuristics.

    Detection signals include:
    - LLM-related keywords (You are, Act as, etc.)
    - Instruction verbs (Analyze, Generate, Summarize)
    - Few-shot patterns (Example:, Input:, Output:)
    - API call patterns (openai.chat.completions.create)
    - Role-based patterns (system:, assistant:, user:)
    - Template markers ({}, f-string, .format())
    """

    # Keywords that indicate LLM prompts
    LLM_KEYWORDS = [
        r"\bYou are\b",
        r"\bAct as\b",
        r"\bAssistant:",
        r"\bSystem:",
        r"\bUser:",
        r"\bopenai\b",
        r"\banthropic\b",
        r"\bclaude\b",
        r"\bgpt-?\d",
        r"\bllm\b",
        r"\bchatbot\b",
        r"\bai assistant\b",
        r"\bprompt\b",
    ]

    # Instruction verbs commonly found in prompts
    INSTRUCTION_VERBS = [
        r"\bAnalyze\b",
        r"\bGenerate\b",
        r"\bTranslate\b",
        r"\bSummarize\b",
        r"\bExplain\b",
        r"\bDescribe\b",
        r"\bWrite\b",
        r"\bCreate\b",
        r"\bList\b",
        r"\bProvide\b",
        r"\bIdentify\b",
        r"\bEvaluate\b",
        r"\bCompare\b",
        r"\bClassify\b",
        r"\bExtract\b",
    ]

    # Few-shot learning patterns
    FEW_SHOT_PATTERNS = [
        r"Example\s*:",
        r"Input\s*:",
        r"Output\s*:",
        r"Q\s*:",
        r"A\s*:",
        r"Question\s*:",
        r"Answer\s*:",
        r"###\s*Example",
        r"Here's an example",
        r"For example",
    ]

    # LLM API call patterns
    API_CALL_PATTERNS = [
        r"openai\.chat\.completions\.create",
        r"openai\.ChatCompletion\.create",
        r"anthropic\.messages\.create",
        r"anthropic\.completions\.create",
        r"client\.chat\.completions",
        r"client\.messages\.create",
        r"model\.generate",
        r"pipeline\(['\"]text-generation",
        r"AutoModelForCausalLM",
        r"\.invoke\(",  # LangChain
        r"ChatOpenAI\(",
        r"ChatAnthropic\(",
        r"HuggingFaceHub\(",
    ]

    # Role-based patterns
    ROLE_PATTERNS = [
        r"role\s*[:=]\s*['\"]system['\"]",
        r"role\s*[:=]\s*['\"]user['\"]",
        r"role\s*[:=]\s*['\"]assistant['\"]",
        r"system_prompt",
        r"user_prompt",
        r"messages\s*=\s*\[",
    ]

    # String assignment patterns that might contain prompts
    STRING_PATTERNS = [
        r'(?:prompt|message|instruction|template)\s*=\s*["\']',
        r'(?:prompt|message|instruction|template)\s*=\s*f["\']',
        r'(?:prompt|message|instruction|template)\s*=\s*"""',
        r"(?:prompt|message|instruction|template)\s*=\s*'''",
    ]

    def __init__(
        self,
        min_confidence: float = 0.3,
        min_length: int = 20,
        max_length: int = 10000,
        use_ast: bool = True,
    ):
        """
        Initialize the prompt detector.

        Args:
            min_confidence: Minimum confidence score to consider a prompt (0-1)
            min_length: Minimum length of text to consider as a prompt
            max_length: Maximum length of text to consider
            use_ast: Whether to use AST-based extraction (more accurate, handles docstrings)
        """
        self.min_confidence = min_confidence
        self.min_length = min_length
        self.max_length = max_length
        self.use_ast = use_ast

        # AST-based extractor for accurate prompt detection
        self._ast_extractor = PromptExtractor(
            min_length=min_length,
            max_length=max_length,
            min_confidence=min_confidence,
        )

        # Compile regex patterns for efficiency (used as fallback)
        self._compiled_patterns = {
            "llm_keywords": [re.compile(p, re.IGNORECASE) for p in self.LLM_KEYWORDS],
            "instruction_verbs": [re.compile(p, re.IGNORECASE) for p in self.INSTRUCTION_VERBS],
            "few_shot_patterns": [re.compile(p, re.IGNORECASE) for p in self.FEW_SHOT_PATTERNS],
            "api_calls": [re.compile(p) for p in self.API_CALL_PATTERNS],
            "role_patterns": [re.compile(p, re.IGNORECASE) for p in self.ROLE_PATTERNS],
            "string_patterns": [re.compile(p, re.IGNORECASE) for p in self.STRING_PATTERNS],
        }

    def detect_prompts(self, file_path: str) -> list[DetectedPrompt]:
        """
        Detect AI prompts in a source file.

        Args:
            file_path: Path to the source file

        Returns:
            List of detected prompts with confidence scores
        """
        path = Path(file_path)

        if not path.exists():
            return []

        # Use AST extractor directly for file-based detection
        if self.use_ast:
            try:
                extracted = self._ast_extractor.extract_from_file(str(path))
                return self._convert_extracted_to_prompts(extracted, path)
            except Exception:
                pass  # Fall back to content-based detection

        # Fallback to content reading
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            return []

        return self.detect_prompts_in_content(content, str(path))

    def _convert_extracted_to_prompts(
        self, extracted: list[ExtractedString], path: Path
    ) -> list[DetectedPrompt]:
        """Convert ExtractedString objects to DetectedPrompt objects."""
        prompts = []

        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            content = ""

        for ext in extracted:
            # Combine AST confidence with signal-based scoring
            signals = self._calculate_signals(ext.content)
            combined_confidence = max(ext.confidence, signals.total_score)

            prompt_type = self._determine_prompt_type_from_context(ext)

            prompts.append(DetectedPrompt(
                content=ext.content,
                location=PromptLocation(
                    file_path=str(path),
                    start_line=ext.start_line,
                    end_line=ext.end_line,
                    start_col=ext.start_col,
                    end_col=ext.end_col,
                ),
                confidence=combined_confidence,
                prompt_type=prompt_type,
                context=self._get_context(content, ext.start_line, ext.end_line) if content else None,
                variable_name=ext.variable_name,
            ))

        return prompts

    def detect_prompts_in_content(self, content: str, file_path: str = "<string>") -> list[DetectedPrompt]:
        """
        Detect AI prompts in content string.

        Args:
            content: Source code content
            file_path: Path for location reporting

        Returns:
            List of detected prompts
        """
        # Try AST-based extraction first (more accurate)
        if self.use_ast:
            try:
                return self._detect_with_ast(content, file_path)
            except Exception:
                # Fall back to regex if AST fails
                pass

        # Fallback to regex-based extraction
        return self._detect_with_regex(content, file_path)

    def _detect_with_ast(self, content: str, file_path: str) -> list[DetectedPrompt]:
        """
        Detect prompts using AST-based extraction.

        This method properly handles:
        - Docstring filtering (module, class, function)
        - Context-aware scoring (variable names, dict keys)
        - Natural language detection
        """
        # Determine file type from path
        suffix = Path(file_path).suffix.lower()

        if suffix == ".py":
            extracted = self._ast_extractor.extract_from_python(content, file_path)
        elif suffix == ".json":
            extracted = self._ast_extractor.extract_from_json(content, file_path)
        elif suffix in (".yaml", ".yml"):
            extracted = self._ast_extractor.extract_from_yaml(content, file_path)
        elif suffix in (".txt", ".md"):
            extracted = self._ast_extractor.extract_from_text(content, file_path)
        else:
            # Try Python parsing for unknown types
            extracted = self._ast_extractor.extract_from_python(content, file_path)

        # Convert ExtractedString to DetectedPrompt
        prompts = []
        for ext in extracted:
            # Combine AST confidence with signal-based scoring
            signals = self._calculate_signals(ext.content)

            # Use the higher confidence (AST context vs. signal patterns)
            combined_confidence = max(ext.confidence, signals.total_score)

            # Determine prompt type from context
            prompt_type = self._determine_prompt_type_from_context(ext)

            prompts.append(DetectedPrompt(
                content=ext.content,
                location=PromptLocation(
                    file_path=file_path,
                    start_line=ext.start_line,
                    end_line=ext.end_line,
                    start_col=ext.start_col,
                    end_col=ext.end_col,
                ),
                confidence=combined_confidence,
                prompt_type=prompt_type,
                context=self._get_context(content, ext.start_line, ext.end_line),
                variable_name=ext.variable_name,
            ))

        return prompts

    def _determine_prompt_type_from_context(self, ext: ExtractedString) -> str:
        """Determine prompt type using AST context information."""
        var_lower = (ext.variable_name or "").lower()
        key_lower = (ext.dict_key or "").lower()
        arg_lower = (ext.argument_name or "").lower()

        # Check variable name
        if "system" in var_lower or key_lower == "system":
            return "system"
        elif "user" in var_lower or key_lower == "user":
            return "user"
        elif "assistant" in var_lower or key_lower == "assistant":
            return "assistant"
        elif "template" in var_lower:
            return "template"

        # Check dict key (for message structures)
        if key_lower == "content":
            return "message"

        # Check argument name
        if arg_lower in ("system", "system_prompt", "system_message"):
            return "system"
        elif arg_lower in ("prompt", "instruction"):
            return "template"

        # Fall back to content analysis
        content_lower = ext.content.lower()
        if content_lower.startswith("you are") or "act as" in content_lower:
            return "system"

        # Check for template markers
        if "{" in ext.content and "}" in ext.content:
            return "template"

        return "unknown"

    def _detect_with_regex(self, content: str, file_path: str) -> list[DetectedPrompt]:
        """
        Detect prompts using regex-based extraction (fallback method).
        """
        prompts = []

        # Find string literals that might be prompts
        string_candidates = self._extract_string_literals(content)

        for text, start_line, end_line, var_name in string_candidates:
            # Skip if too short or too long
            if len(text) < self.min_length or len(text) > self.max_length:
                continue

            # Calculate detection signals
            signals = self._calculate_signals(text)
            confidence = signals.total_score

            if confidence >= self.min_confidence:
                # Determine prompt type
                prompt_type = self._determine_prompt_type(text, var_name)

                # Get surrounding context
                context = self._get_context(content, start_line, end_line)

                prompts.append(DetectedPrompt(
                    content=text,
                    location=PromptLocation(
                        file_path=file_path,
                        start_line=start_line,
                        end_line=end_line,
                    ),
                    confidence=confidence,
                    prompt_type=prompt_type,
                    context=context,
                    variable_name=var_name,
                ))

        return prompts

    def _extract_string_literals(self, content: str) -> list[tuple[str, int, int, Optional[str]]]:
        """
        Extract string literals from source code.

        Returns list of (text, start_line, end_line, variable_name) tuples.
        """
        results = []
        content.split("\n")

        # Pattern for multi-line strings (triple quotes)
        triple_quote_pattern = re.compile(
            r'(?:(\w+)\s*=\s*)?("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')',
            re.MULTILINE
        )

        # Pattern for f-strings and regular strings
        string_pattern = re.compile(
            r'(?:(\w+)\s*=\s*)?(f?["\'](?:[^"\'\\]|\\.)*["\'])',
        )

        # Find triple-quoted strings
        for match in triple_quote_pattern.finditer(content):
            var_name = match.group(1)
            text = match.group(2)

            # Clean the text (remove quotes)
            if text.startswith('"""'):
                text = text[3:-3]
            else:
                text = text[3:-3]

            # Calculate line numbers
            start_pos = match.start()
            start_line = content[:start_pos].count("\n") + 1
            end_line = start_line + text.count("\n")

            results.append((text, start_line, end_line, var_name))

        # Find regular strings that are long enough
        for match in string_pattern.finditer(content):
            var_name = match.group(1)
            text = match.group(2)

            # Clean the text (remove quotes and f prefix)
            if text.startswith("f"):
                text = text[1:]
            text = text[1:-1]  # Remove quotes

            # Only include if it's substantial
            if len(text) >= self.min_length:
                start_pos = match.start()
                start_line = content[:start_pos].count("\n") + 1
                end_line = start_line

                results.append((text, start_line, end_line, var_name))

        return results

    def _calculate_signals(self, text: str) -> DetectionSignals:
        """Calculate detection signals for a text."""
        return DetectionSignals(
            llm_keywords=sum(1 for p in self._compiled_patterns["llm_keywords"] if p.search(text)),
            instruction_verbs=sum(1 for p in self._compiled_patterns["instruction_verbs"] if p.search(text)),
            few_shot_patterns=sum(1 for p in self._compiled_patterns["few_shot_patterns"] if p.search(text)),
            api_calls=sum(1 for p in self._compiled_patterns["api_calls"] if p.search(text)),
            role_patterns=sum(1 for p in self._compiled_patterns["role_patterns"] if p.search(text)),
            template_markers=self._count_template_markers(text),
            length_score=self._calculate_length_score(text),
        )

    def _count_template_markers(self, text: str) -> int:
        """Count template variable markers in text."""
        count = 0

        # {variable} style
        count += len(re.findall(r"\{[^}]+\}", text))

        # {{variable}} style (Jinja2)
        count += len(re.findall(r"\{\{[^}]+\}\}", text))

        # $variable style
        count += len(re.findall(r"\$\w+", text))

        return count

    def _calculate_length_score(self, text: str) -> float:
        """
        Calculate a length-based score.

        Prompts are typically between 50-2000 characters.
        """
        length = len(text)

        if length < self.min_length:
            return 0.0
        elif length < 100:
            return 0.3
        elif length < 500:
            return 0.8
        elif length < 2000:
            return 1.0
        elif length < 5000:
            return 0.7
        else:
            return 0.4

    def _determine_prompt_type(self, text: str, var_name: Optional[str]) -> str:
        """Determine the type of prompt based on content and variable name."""
        text_lower = text.lower()
        var_lower = (var_name or "").lower()

        # Check variable name first
        if "system" in var_lower:
            return "system"
        elif "user" in var_lower:
            return "user"
        elif "template" in var_lower:
            return "template"

        # Check content
        if text_lower.startswith("you are") or "act as" in text_lower:
            return "system"
        elif any(p in text_lower for p in ["example:", "input:", "output:"]):
            return "few_shot"
        elif "{" in text and "}" in text:
            return "template"

        return "unknown"

    def _get_context(self, content: str, start_line: int, end_line: int, context_lines: int = 3) -> str:
        """Get surrounding code context."""
        lines = content.split("\n")

        ctx_start = max(0, start_line - context_lines - 1)
        ctx_end = min(len(lines), end_line + context_lines)

        return "\n".join(lines[ctx_start:ctx_end])

    def quick_check(self, content: str) -> bool:
        """
        Quick check if content likely contains prompts.

        This is a fast pre-filter before deeper analysis.
        """
        # Check for common LLM-related patterns
        quick_patterns = [
            r"You are",
            r"Act as",
            r"system_prompt",
            r"user_prompt",
            r"openai\.",
            r"anthropic\.",
            r"messages\s*=",
        ]

        for pattern in quick_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        return False
