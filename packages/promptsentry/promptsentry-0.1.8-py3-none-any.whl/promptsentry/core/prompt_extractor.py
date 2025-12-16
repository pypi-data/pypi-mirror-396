"""
AST-based Prompt Extractor

Comprehensive prompt detection using Python AST analysis with context scoring.
This module replaces simple regex-based string extraction with intelligent
analysis that understands code structure.

Features:
- Proper docstring filtering (module, class, function)
- Context-aware scoring based on variable names, dict keys, function arguments
- Non-Python file support (JSON, YAML, TXT, TOML)
- Natural language detection to filter out code artifacts
- Confidence scoring with multiple signals
"""

import ast
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class ExtractionContext(str, Enum):
    """Context in which a string was found."""
    VARIABLE_ASSIGNMENT = "variable_assignment"
    FUNCTION_ARGUMENT = "function_argument"
    DICT_VALUE = "dict_value"
    LIST_ELEMENT = "list_element"
    RETURN_VALUE = "return_value"
    CLASS_ATTRIBUTE = "class_attribute"
    MODULE_LEVEL = "module_level"
    UNKNOWN = "unknown"


@dataclass
class ExtractedString:
    """A string extracted from source code with context."""
    content: str
    start_line: int
    end_line: int
    start_col: int = 0
    end_col: int = 0
    
    # Context information
    context: ExtractionContext = ExtractionContext.UNKNOWN
    variable_name: Optional[str] = None
    dict_key: Optional[str] = None
    function_name: Optional[str] = None
    argument_name: Optional[str] = None
    parent_class: Optional[str] = None
    
    # Scoring
    confidence: float = 0.0
    is_docstring: bool = False
    signals: dict = field(default_factory=dict)


class PromptExtractor:
    """
    AST-based extractor for identifying AI prompts in source code.
    
    Uses Python's AST module to properly parse code structure, avoiding
    false positives from docstrings and non-prompt strings.
    """
    
    # High-confidence variable names
    HIGH_CONFIDENCE_NAMES = {
        "prompt", "system_prompt", "user_prompt", "assistant_prompt",
        "instruction", "instructions", "system_message", "user_message",
        "system_instruction", "context_prompt", "template", "prompt_template",
        "base_prompt", "initial_prompt", "final_prompt", "full_prompt",
    }
    
    # Medium-confidence variable names (need content analysis)
    MEDIUM_CONFIDENCE_NAMES = {
        "message", "messages", "content", "text", "query", "input_text",
        "context", "description", "request", "command", "task",
    }
    
    # High-confidence dict keys
    HIGH_CONFIDENCE_KEYS = {
        "prompt", "system", "instruction", "system_prompt", "system_message",
        "user_prompt", "template", "context",
    }
    
    # Dict keys that indicate LLM message structure
    MESSAGE_STRUCTURE_KEYS = {"role", "content"}
    
    # Function names that take prompts
    PROMPT_FUNCTIONS = {
        "format_prompt", "build_prompt", "create_prompt", "get_prompt",
        "generate_prompt", "make_prompt", "prepare_prompt",
    }
    
    # API functions that use prompts
    API_FUNCTIONS = {
        "create", "chat", "complete", "completion", "generate",
        "invoke", "run", "call", "send", "ask",
    }
    
    # Patterns that indicate non-natural language (to filter out)
    NON_NATURAL_PATTERNS = [
        r'^https?://',  # URLs
        r'^/[\w/]+$',  # File paths
        r'^\w+\.\w+\.\w+',  # Module paths
        r'^[A-Z_]+$',  # Constants
        r'^\d+$',  # Numbers
        r'^[\w-]+\.(?:py|js|ts|json|yaml|yml|txt|md|css|html)$',  # File names
        r'^SELECT\s|^INSERT\s|^UPDATE\s|^DELETE\s|^CREATE\s',  # SQL
        r'^[{}\[\]]+$',  # JSON/brackets only
        r'^\s*(?:#|//|/\*)',  # Comments
        r'^[a-z_]+$',  # Single word lowercase (likely identifier)
        r'^[A-Z][a-z]+(?:[A-Z][a-z]+)+$',  # CamelCase (likely class name)
    ]
    
    # Patterns that indicate natural language (prompts)
    NATURAL_LANGUAGE_PATTERNS = [
        r'\b(?:you are|act as|you\'re)\b',
        r'\b(?:please|help|assist|analyze|generate|explain|summarize)\b',
        r'\b(?:the|a|an|is|are|was|were|will|would|could|should)\b',
        r'[.!?]',  # Sentence endings
        r'\b(?:user|assistant|system|human|ai)\b',
    ]
    
    def __init__(
        self,
        min_length: int = 20,
        max_length: int = 50000,
        min_confidence: float = 0.4,
    ):
        """
        Initialize the prompt extractor.
        
        Args:
            min_length: Minimum string length to consider
            max_length: Maximum string length to consider  
            min_confidence: Minimum confidence to return a string
        """
        self.min_length = min_length
        self.max_length = max_length
        self.min_confidence = min_confidence
        
        # Compile patterns
        self._non_natural = [re.compile(p, re.IGNORECASE) for p in self.NON_NATURAL_PATTERNS]
        self._natural = [re.compile(p, re.IGNORECASE) for p in self.NATURAL_LANGUAGE_PATTERNS]
    
    def extract_from_file(self, file_path: str) -> list[ExtractedString]:
        """
        Extract potential prompts from a file.
        
        Routes to appropriate handler based on file extension.
        """
        path = Path(file_path)
        
        if not path.exists():
            return []
        
        suffix = path.suffix.lower()
        
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            return []
        
        # Route to appropriate handler
        if suffix == ".py":
            return self.extract_from_python(content, str(path))
        elif suffix in (".json",):
            return self.extract_from_json(content, str(path))
        elif suffix in (".yaml", ".yml"):
            return self.extract_from_yaml(content, str(path))
        elif suffix in (".txt", ".md"):
            return self.extract_from_text(content, str(path))
        elif suffix == ".toml":
            return self.extract_from_toml(content, str(path))
        else:
            # For unknown types, try Python first (might be a script without extension)
            try:
                return self.extract_from_python(content, str(path))
            except SyntaxError:
                return []
    
    def extract_from_python(self, content: str, file_path: str = "<string>") -> list[ExtractedString]:
        """
        Extract strings from Python source code using AST.
        
        This properly handles:
        - Module/class/function docstrings (filtered out)
        - Variable assignments with context
        - Dictionary values with key context
        - Function arguments with position/keyword context
        """
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []
        
        strings = []
        lines = content.split("\n")
        
        # Track docstrings to filter them out
        docstring_positions = self._find_docstrings(tree)
        
        # Track processed nodes to avoid duplicates (e.g., f-strings in assignments)
        processed_nodes: set[int] = set()
        
        # Walk the AST
        for node in ast.walk(tree):
            extracted = self._extract_from_node(node, tree, docstring_positions, processed_nodes)
            strings.extend(extracted)
        
        # Calculate confidence scores
        for s in strings:
            s.confidence = self._calculate_confidence(s, content)
        
        # Filter by length, confidence, and docstring status
        filtered = [
            s for s in strings
            if (
                len(s.content) >= self.min_length
                and len(s.content) <= self.max_length
                and s.confidence >= self.min_confidence
                and not s.is_docstring
            )
        ]
        
        return filtered
    
    def _find_docstrings(self, tree: ast.AST) -> set[tuple[int, int]]:
        """Find all docstring positions in the AST."""
        docstrings = set()
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check for docstring (first statement that's a string expr)
                body = getattr(node, 'body', [])
                if body and isinstance(body[0], ast.Expr):
                    expr_value = body[0].value
                    if isinstance(expr_value, ast.Constant) and isinstance(expr_value.value, str):
                        docstrings.add((expr_value.lineno, expr_value.col_offset))
        
        return docstrings
    
    def _extract_from_node(
        self,
        node: ast.AST,
        tree: ast.AST,
        docstring_positions: set[tuple[int, int]],
        processed_nodes: set[int],
    ) -> list[ExtractedString]:
        """Extract strings from an AST node with context."""
        strings = []
        
        # Variable assignment: x = "string" or x = f"string {var}"
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    
                    # Regular string assignment
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        s = self._create_extracted_string(
                            node.value,
                            context=ExtractionContext.VARIABLE_ASSIGNMENT,
                            variable_name=var_name,
                            docstring_positions=docstring_positions,
                        )
                        if s:
                            strings.append(s)
                    
                    # F-string assignment
                    elif isinstance(node.value, ast.JoinedStr):
                        s = self._extract_fstring(node.value, var_name)
                        if s:
                            strings.append(s)
                            # Mark this JoinedStr as processed to avoid duplicates
                            processed_nodes.add(id(node.value))
        
        # Annotated assignment: x: str = "string"
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.value and isinstance(node.value, ast.Constant):
                if isinstance(node.value.value, str):
                    var_name = node.target.id
                    s = self._create_extracted_string(
                        node.value,
                        context=ExtractionContext.VARIABLE_ASSIGNMENT,
                        variable_name=var_name,
                        docstring_positions=docstring_positions,
                    )
                    if s:
                        strings.append(s)
        
        # Dictionary: {"key": "value"}
        elif isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    key_name = key.value
                    if isinstance(value, ast.Constant) and isinstance(value.value, str):
                        s = self._create_extracted_string(
                            value,
                            context=ExtractionContext.DICT_VALUE,
                            dict_key=key_name,
                            docstring_positions=docstring_positions,
                        )
                        if s:
                            strings.append(s)
        
        # Function call: func("string") or func(arg="string")
        elif isinstance(node, ast.Call):
            func_name = self._get_func_name(node.func)
            
            # Positional arguments
            for i, arg in enumerate(node.args):
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    s = self._create_extracted_string(
                        arg,
                        context=ExtractionContext.FUNCTION_ARGUMENT,
                        function_name=func_name,
                        argument_name=f"arg_{i}",
                        docstring_positions=docstring_positions,
                    )
                    if s:
                        strings.append(s)
            
            # Keyword arguments
            for kw in node.keywords:
                if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                    s = self._create_extracted_string(
                        kw.value,
                        context=ExtractionContext.FUNCTION_ARGUMENT,
                        function_name=func_name,
                        argument_name=kw.arg,
                        docstring_positions=docstring_positions,
                    )
                    if s:
                        strings.append(s)
        
        # List: ["string1", "string2"]
        elif isinstance(node, ast.List):
            for elt in node.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    s = self._create_extracted_string(
                        elt,
                        context=ExtractionContext.LIST_ELEMENT,
                        docstring_positions=docstring_positions,
                    )
                    if s:
                        strings.append(s)
        
        # Return statement: return "string"
        elif isinstance(node, ast.Return):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                s = self._create_extracted_string(
                    node.value,
                    context=ExtractionContext.RETURN_VALUE,
                    docstring_positions=docstring_positions,
                )
                if s:
                    strings.append(s)
        
        # JoinedStr (f-strings): f"Hello {name}" - only if not already captured via Assign
        # Note: F-strings in assignments are handled above, this catches others
        elif isinstance(node, ast.JoinedStr):
            # Skip if already processed (e.g., as part of an assignment)
            if id(node) in processed_nodes:
                return strings
            
            # Extract standalone f-string
            s = self._extract_fstring(node, variable_name=None)
            if s:
                strings.append(s)
        
        return strings
    
    def _extract_fstring(
        self,
        node: ast.JoinedStr,
        variable_name: Optional[str] = None,
    ) -> Optional[ExtractedString]:
        """Extract content from an f-string node."""
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant):
                parts.append(str(value.value))
            elif isinstance(value, ast.FormattedValue):
                # Try to get the variable name if it's simple
                if isinstance(value.value, ast.Name):
                    parts.append(f"{{{value.value.id}}}")
                else:
                    parts.append("{...}")
        
        content = "".join(parts)
        if not content:
            return None
        
        context = ExtractionContext.VARIABLE_ASSIGNMENT if variable_name else ExtractionContext.UNKNOWN
        
        return ExtractedString(
            content=content,
            start_line=node.lineno,
            end_line=getattr(node, 'end_lineno', node.lineno) or node.lineno,
            start_col=node.col_offset,
            end_col=getattr(node, 'end_col_offset', 0) or 0,
            context=context,
            variable_name=variable_name,
        )
    
    def _create_extracted_string(
        self,
        node: ast.Constant,
        context: ExtractionContext,
        variable_name: Optional[str] = None,
        dict_key: Optional[str] = None,
        function_name: Optional[str] = None,
        argument_name: Optional[str] = None,
        docstring_positions: Optional[set] = None,
    ) -> Optional[ExtractedString]:
        """Create an ExtractedString from an AST Constant node."""
        if not isinstance(node.value, str):
            return None
        
        is_docstring = False
        if docstring_positions:
            is_docstring = (node.lineno, node.col_offset) in docstring_positions
        
        return ExtractedString(
            content=node.value,
            start_line=node.lineno,
            end_line=getattr(node, 'end_lineno', node.lineno) or node.lineno,
            start_col=node.col_offset,
            end_col=getattr(node, 'end_col_offset', 0) or 0,
            context=context,
            variable_name=variable_name,
            dict_key=dict_key,
            function_name=function_name,
            argument_name=argument_name,
            is_docstring=is_docstring,
        )
    
    def _get_func_name(self, node: ast.expr) -> str:
        """Extract function name from a call expression."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # For x.method(), return "method"
            return node.attr
        elif isinstance(node, ast.Call):
            # For nested calls
            return self._get_func_name(node.func)
        return "unknown"
    
    def _calculate_confidence(self, s: ExtractedString, content: str) -> float:
        """
        Calculate confidence score for an extracted string.
        
        Scoring factors:
        - Variable/key name matching
        - Natural language patterns
        - Length appropriateness
        - Context (API calls, message dicts, etc.)
        """
        score = 0.0
        signals = {}
        
        # === Variable Name Scoring ===
        var_name_lower = (s.variable_name or "").lower()
        if var_name_lower in self.HIGH_CONFIDENCE_NAMES:
            score += 0.5
            signals["high_conf_var"] = var_name_lower
        elif var_name_lower in self.MEDIUM_CONFIDENCE_NAMES:
            score += 0.25
            signals["medium_conf_var"] = var_name_lower
        elif any(kw in var_name_lower for kw in ("prompt", "instruction", "system", "message")):
            score += 0.35
            signals["partial_var_match"] = var_name_lower
        
        # === Dict Key Scoring ===
        dict_key_lower = (s.dict_key or "").lower()
        if dict_key_lower in self.HIGH_CONFIDENCE_KEYS:
            score += 0.45
            signals["high_conf_key"] = dict_key_lower
        elif dict_key_lower == "content":
            # Special handling for "content" - check if sibling has "role"
            score += 0.35
            signals["content_key"] = True
        
        # === Function Context Scoring ===
        func_name_lower = (s.function_name or "").lower()
        if func_name_lower in self.PROMPT_FUNCTIONS:
            score += 0.4
            signals["prompt_function"] = func_name_lower
        elif func_name_lower in self.API_FUNCTIONS:
            score += 0.35
            signals["api_function"] = func_name_lower
        
        # Argument name scoring
        arg_name_lower = (s.argument_name or "").lower()
        if arg_name_lower in ("prompt", "system", "instruction", "message", "content"):
            score += 0.4
            signals["prompt_argument"] = arg_name_lower
        
        # === Content Analysis ===
        text = s.content.lower()
        
        # Check for non-natural language patterns (reduces score)
        non_natural_count = sum(1 for p in self._non_natural if p.search(text))
        if non_natural_count > 0:
            score -= 0.3 * min(non_natural_count, 2)
            signals["non_natural"] = non_natural_count
        
        # Check for natural language patterns (increases score)
        natural_count = sum(1 for p in self._natural if p.search(text))
        if natural_count > 0:
            score += 0.1 * min(natural_count, 4)
            signals["natural_patterns"] = natural_count
        
        # === Length Scoring ===
        length = len(s.content)
        if 50 <= length <= 500:
            score += 0.2
            signals["ideal_length"] = True
        elif 500 < length <= 2000:
            score += 0.15
            signals["long_prompt"] = True
        elif length > 2000:
            score += 0.1
            signals["very_long"] = True
        elif 20 <= length < 50:
            score += 0.05
            signals["short"] = True
        
        # === Special Pattern Detection ===
        
        # LLM keywords
        llm_patterns = [
            r'\b(?:you are|you\'re)\b',
            r'\bact as\b',
            r'\b(?:openai|anthropic|claude|gpt)\b',
            r'\b(?:assistant|system|user)\s*:',
        ]
        llm_count = sum(1 for p in llm_patterns if re.search(p, text, re.IGNORECASE))
        if llm_count > 0:
            score += 0.15 * min(llm_count, 3)
            signals["llm_keywords"] = llm_count
        
        # Instruction verbs
        instruction_verbs = [
            r'\b(?:analyze|generate|summarize|explain|describe|write|create|list|provide|extract)\b'
        ]
        verb_count = sum(1 for p in instruction_verbs if re.search(p, text, re.IGNORECASE))
        if verb_count > 0:
            score += 0.1 * min(verb_count, 3)
            signals["instruction_verbs"] = verb_count
        
        # Template markers
        template_count = len(re.findall(r'\{[^}]+\}', s.content))
        if template_count > 0:
            score += 0.1
            signals["template_markers"] = template_count
        
        s.signals = signals
        return min(max(score, 0.0), 1.0)
    
    # ===== Non-Python File Handlers =====
    
    def extract_from_json(self, content: str, file_path: str = "<string>") -> list[ExtractedString]:
        """Extract prompt-like strings from JSON content."""
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return []
        
        strings = []
        self._extract_from_json_value(data, strings, file_path, [], 1)
        
        # Calculate confidence for each
        for s in strings:
            s.confidence = self._calculate_confidence(s, content)
        
        return [
            s for s in strings
            if len(s.content) >= self.min_length
            and s.confidence >= self.min_confidence
        ]
    
    def _extract_from_json_value(
        self,
        value: Any,
        strings: list[ExtractedString],
        file_path: str,
        path: list[str],
        line: int,
    ) -> None:
        """Recursively extract strings from JSON structure."""
        if isinstance(value, str):
            key = path[-1] if path else None
            s = ExtractedString(
                content=value,
                start_line=line,
                end_line=line,
                context=ExtractionContext.DICT_VALUE if key else ExtractionContext.LIST_ELEMENT,
                dict_key=key,
            )
            strings.append(s)
        elif isinstance(value, dict):
            for k, v in value.items():
                self._extract_from_json_value(v, strings, file_path, path + [k], line)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                self._extract_from_json_value(item, strings, file_path, path + [f"[{i}]"], line)
    
    def extract_from_yaml(self, content: str, file_path: str = "<string>") -> list[ExtractedString]:
        """Extract prompt-like strings from YAML content."""
        try:
            import yaml
            data = yaml.safe_load(content)
        except Exception:
            return []
        
        if data is None:
            return []
        
        strings = []
        self._extract_from_json_value(data, strings, file_path, [], 1)  # Reuse JSON logic
        
        # Calculate confidence
        for s in strings:
            s.confidence = self._calculate_confidence(s, content)
        
        return [
            s for s in strings
            if len(s.content) >= self.min_length
            and s.confidence >= self.min_confidence
        ]
    
    def extract_from_toml(self, content: str, file_path: str = "<string>") -> list[ExtractedString]:
        """Extract prompt-like strings from TOML content."""
        try:
            import tomllib
            data = tomllib.loads(content)
        except Exception:
            try:
                # Fallback for Python < 3.11
                import tomli as tomllib
                data = tomllib.loads(content)
            except Exception:
                return []
        
        strings = []
        self._extract_from_json_value(data, strings, file_path, [], 1)
        
        for s in strings:
            s.confidence = self._calculate_confidence(s, content)
        
        return [
            s for s in strings
            if len(s.content) >= self.min_length
            and s.confidence >= self.min_confidence
        ]
    
    def extract_from_text(self, content: str, file_path: str = "<string>") -> list[ExtractedString]:
        """
        Extract from plain text files (prompts.txt, system_message.md, etc.).
        
        For text files, we treat the entire content as a potential prompt
        if it meets length and natural language criteria.
        """
        content = content.strip()
        
        if len(content) < self.min_length:
            return []
        
        # Check if it looks like natural language / prompt
        s = ExtractedString(
            content=content,
            start_line=1,
            end_line=content.count("\n") + 1,
            context=ExtractionContext.MODULE_LEVEL,
        )
        
        # Boost confidence if filename suggests prompt
        file_name = Path(file_path).stem.lower()
        if any(kw in file_name for kw in ("prompt", "instruction", "system", "template")):
            s.variable_name = file_name  # Use filename as variable for scoring
        
        s.confidence = self._calculate_confidence(s, content)
        
        if s.confidence >= self.min_confidence:
            return [s]
        
        return []


def extract_prompts_from_file(file_path: str, min_confidence: float = 0.4) -> list[ExtractedString]:
    """
    Convenience function to extract prompts from a file.
    
    Args:
        file_path: Path to the file
        min_confidence: Minimum confidence threshold
    
    Returns:
        List of extracted strings that are likely prompts
    """
    extractor = PromptExtractor(min_confidence=min_confidence)
    return extractor.extract_from_file(file_path)


def extract_prompts_from_content(
    content: str,
    file_type: str = "python",
    min_confidence: float = 0.4,
) -> list[ExtractedString]:
    """
    Extract prompts from content string.
    
    Args:
        content: Source code or text content
        file_type: Type of file ("python", "json", "yaml", "text")
        min_confidence: Minimum confidence threshold
    
    Returns:
        List of extracted strings
    """
    extractor = PromptExtractor(min_confidence=min_confidence)
    
    if file_type == "python":
        return extractor.extract_from_python(content)
    elif file_type == "json":
        return extractor.extract_from_json(content)
    elif file_type in ("yaml", "yml"):
        return extractor.extract_from_yaml(content)
    elif file_type in ("text", "txt", "md"):
        return extractor.extract_from_text(content)
    else:
        return extractor.extract_from_python(content)

