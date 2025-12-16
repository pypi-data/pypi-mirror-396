"""
Stage 1: Prompt Detector

Quickly identifies AI prompts in source code using heuristics and pattern matching.
This is the first stage of the PromptSentry pipeline - a fast filter to identify
files that need deeper analysis.
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple

from promptsentry.models.detection import DetectedPrompt, PromptLocation, DetectionSignals


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
    
    def __init__(self, min_confidence: float = 0.3, min_length: int = 20, max_length: int = 10000):
        """
        Initialize the prompt detector.
        
        Args:
            min_confidence: Minimum confidence score to consider a prompt (0-1)
            min_length: Minimum length of text to consider as a prompt
            max_length: Maximum length of text to consider
        """
        self.min_confidence = min_confidence
        self.min_length = min_length
        self.max_length = max_length
        
        # Compile regex patterns for efficiency
        self._compiled_patterns = {
            "llm_keywords": [re.compile(p, re.IGNORECASE) for p in self.LLM_KEYWORDS],
            "instruction_verbs": [re.compile(p, re.IGNORECASE) for p in self.INSTRUCTION_VERBS],
            "few_shot_patterns": [re.compile(p, re.IGNORECASE) for p in self.FEW_SHOT_PATTERNS],
            "api_calls": [re.compile(p) for p in self.API_CALL_PATTERNS],
            "role_patterns": [re.compile(p, re.IGNORECASE) for p in self.ROLE_PATTERNS],
            "string_patterns": [re.compile(p, re.IGNORECASE) for p in self.STRING_PATTERNS],
        }
    
    def detect_prompts(self, file_path: str) -> List[DetectedPrompt]:
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
        
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            return []
        
        return self.detect_prompts_in_content(content, str(path))
    
    def detect_prompts_in_content(self, content: str, file_path: str = "<string>") -> List[DetectedPrompt]:
        """
        Detect AI prompts in content string.
        
        Args:
            content: Source code content
            file_path: Path for location reporting
            
        Returns:
            List of detected prompts
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
    
    def _extract_string_literals(self, content: str) -> List[Tuple[str, int, int, Optional[str]]]:
        """
        Extract string literals from source code.
        
        Returns list of (text, start_line, end_line, variable_name) tuples.
        """
        results = []
        lines = content.split("\n")
        
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
