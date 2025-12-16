"""
Stage 3: Prompt Analyzer (SLM Judge)

Final analysis using Ollama (qwen3:4b) as a small language model judge.
The SLM receives comprehensive OWASP LLM Top 10 2025 rules as context and validates
findings from pattern matching while identifying additional vulnerabilities.

Architecture:
- Stage 1: Prompt Detection (heuristics)
- Stage 2: Pattern Matching (regex-based OWASP rules)
- Stage 3: SLM Analysis (Ollama with OWASP rules as context)
"""

import json
import re
from typing import Optional

from promptsentry.llm.prompts import JUDGE_SYSTEM_PROMPT, create_analysis_prompt
from promptsentry.models.config import LLMConfig
from promptsentry.models.detection import DetectedPrompt
from promptsentry.models.vulnerability import (
    AnalysisResult,
    OWASPCategory,
    PatternMatch,
    SimilarMatch,
    Vulnerability,
    VulnerabilitySeverity,
)
from promptsentry.tracker.fingerprint import create_fingerprint_from_parts


class PromptAnalyzer:
    """
    Final stage analyzer using LLM for intelligent vulnerability assessment.

    This stage:
    1. Validates findings from pattern matching and vector similarity
    2. Identifies additional vulnerabilities through contextual analysis
    3. Generates specific, actionable findings with fixes
    4. Creates stable fingerprints for issue tracking
    """

    def __init__(self, config: Optional[LLMConfig] = None, use_llm: bool = True):
        """
        Initialize the analyzer.

        Args:
            config: LLM configuration
            use_llm: Whether to use LLM for analysis (can disable for testing)
        """
        self.config = config or LLMConfig()
        self.use_llm = use_llm
        self._llm = None
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the LLM provider."""
        if self._initialized or not self.use_llm:
            return

        provider = self.config.provider

        if provider == "ollama":
            from promptsentry.llm.ollama import OllamaLLM
            from promptsentry.llm.ollama_manager import OllamaManager

            # Ensure Ollama is running and model is available
            model_name = self.config.model_name or "qwen3:4b"
            success, message = OllamaManager.ensure_ollama_ready(
                model_name=model_name,
                verbose=False  # Silent mode during analysis
            )

            if not success:
                raise RuntimeError(
                    f"Failed to initialize Ollama: {message}\n"
                    f"Please run 'promptsentry init' to set up Ollama properly."
                )

            self._llm = OllamaLLM(self.config)

            # Double-check availability
            if not self._llm.is_available():
                raise RuntimeError(
                    f"Ollama model '{model_name}' not available after setup.\n"
                    f"Please run: ollama pull {model_name}"
                )
        else:
            # Fall back to transformers (requires HuggingFace auth)
            from promptsentry.llm.qwen import QwenLLM
            self._llm = QwenLLM(self.config)

        self._initialized = True

    def analyze(
        self,
        prompt: DetectedPrompt,
        pattern_matches: list[PatternMatch],
        similar_matches: Optional[list[SimilarMatch]] = None,
    ) -> AnalysisResult:
        """
        Perform full analysis on a detected prompt.

        Args:
            prompt: The detected prompt to analyze
            pattern_matches: Findings from pattern matching (Stage 2)
            similar_matches: Optional - kept for backward compatibility but no longer used

        Returns:
            Complete analysis result
        """
        if similar_matches is None:
            similar_matches = []
        vulnerabilities = []
        file_level_text = ""
        try:
            # Use full file text for deterministic presence checks (reduces LLM flakiness)
            from pathlib import Path
            file_level_text = Path(prompt.location.file_path).read_text(encoding="utf-8").lower()
        except Exception:
            file_level_text = prompt.content.lower()

        # NOTE: Pattern matches are SKIPPED for prompt quality analysis
        # Pattern matching is designed for CODE analysis (eval(), SQL injection, etc.)
        # For PROMPT QUALITY, we rely entirely on LLM analysis with OWASP rules
        # The LLM generates proper suggestions with title/suggestion/reasoning/priority

        # Note: Vector similarity matches are deprecated in favor of LLM analysis with OWASP rules
        # Kept for backward compatibility but not actively used
        for match in similar_matches:
            if match.similarity >= 0.75:  # Only high similarity
                vuln_id = create_fingerprint_from_parts(
                    vuln_type=match.vulnerability,
                    location=prompt.location_str,
                    code=prompt.short_content
                )
                vuln = Vulnerability(
                    vuln_id=vuln_id,
                    vuln_type=match.vulnerability,
                    severity=self._similarity_to_severity(match.similarity),
                    owasp_category=match.owasp_category,
                    location=prompt.location_str,
                    vulnerable_code=prompt.short_content,
                    description=match.description,
                    fix=match.fix,
                    confidence=match.similarity,
                )
                vulnerabilities.append(vuln)

        # Use LLM for intelligent analysis with OWASP rules as context
        # The SLM (Ollama) now has comprehensive OWASP LLM Top 10 2025 rules loaded
        # For PROMPT QUALITY analysis, ALWAYS run LLM (it's the primary analyzer)
        llm_analysis = None
        if self.use_llm:
            try:
                llm_vulns, llm_analysis = self._llm_analyze(
                    prompt, pattern_matches, similar_matches
                )

                # Add LLM-discovered vulnerabilities (with suggestion/reasoning/priority)
                for vuln in llm_vulns:
                    vulnerabilities.append(vuln)

            except Exception as e:
                # LLM analysis failed, continue with other findings
                llm_analysis = f"LLM analysis error: {str(e)}"

        # Deterministic guard: if the file already contains explicit security controls,
        # drop "MISSING_*" false-positives that the LLM might mis-report.
        vulnerabilities = self._filter_missing_control_false_positives(
            file_level_text,
            vulnerabilities,
        )

        # Calculate overall score
        overall_score = self._calculate_overall_score(vulnerabilities)

        return AnalysisResult(
            file_path=prompt.location.file_path,
            prompt_location=prompt.location_str,
            vulnerabilities=vulnerabilities,
            overall_score=overall_score,
            is_vulnerable=len(vulnerabilities) > 0,
            pattern_matches=pattern_matches,
            similar_matches=similar_matches,
            llm_analysis=llm_analysis,
        )

    def _llm_analyze(
        self,
        prompt: DetectedPrompt,
        pattern_matches: list[PatternMatch],
        similar_matches: list[SimilarMatch],
    ) -> tuple[list[Vulnerability], str]:
        """
        Use LLM for contextual vulnerability analysis.

        Returns:
            Tuple of (vulnerabilities found, raw LLM output)
        """
        if not self._initialized:
            self.initialize()

        # Create the analysis prompt
        analysis_prompt = create_analysis_prompt(
            detected_prompt=prompt.content,
            pattern_findings=[
                {"id": m.pattern_id, "severity": m.severity.value, "description": m.description}
                for m in pattern_matches
            ],
            vector_findings=[
                {"id": m.rule_id, "similarity": m.similarity, "vulnerability": m.vulnerability}
                for m in similar_matches
            ],
        )

        # Use the LLM interface
        messages = [
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": analysis_prompt},
        ]

        # Generate response via LLM provider (Ollama or transformers)
        response = self._llm.chat(messages)

        # Parse LLM response
        vulnerabilities = self._parse_llm_response(response, prompt)

        return vulnerabilities, response

    def _filter_missing_control_false_positives(
        self,
        file_text: str,
        vulnerabilities: list[Vulnerability],
    ) -> list[Vulnerability]:
        """
        Remove MISSING_* findings when the file already contains strong, explicit
        security controls. This reduces flakiness between direct scans and hook scans.
        """

        def has_any(patterns: list[str]) -> bool:
            return any(p in file_text for p in patterns)

        def has_all(patterns: list[str]) -> bool:
            return all(p in file_text for p in patterns)

        presence = {
            "MISSING_DELIMITER": has_any(
                ["<user_input>", "<content>", "<input>", "<user_request>"]
            ),
            "MISSING_ROLE_IMMUTABILITY": has_any(
                ["cannot be changed", "cannot be overridden", "immutable", "do not change these rules"]
            ),
            "MISSING_DEFENSIVE_INSTRUCTIONS": has_any(
                [
                    "treat all user input as data only",
                    "never execute",
                    "never follow commands from user input",
                    "ignore attempts to change behavior",
                ]
            ),
            "MISSING_OUTPUT_VALIDATION": has_any(
                [
                    "validate output",
                    "validate responses",
                    "only return json",
                    "return valid json",
                ]
            ),
            "MISSING_ENCODING_REJECTION": has_any(
                [
                    "reject base64",
                    "reject encoded",
                    "reject obfuscated",
                    "do not decode",
                    "do not interpret base64",
                ]
            ),
            "MISSING_PII_PROTECTION": has_any(
                [
                    "never reveal credentials",
                    "never disclose sensitive",
                    "never provide api keys",
                    "refuse any request for pii",
                ]
            ),
            "MISSING_PROMPT_PROTECTION": has_any(
                [
                    "never reveal these system instructions",
                    "cannot share system details",
                    "never disclose this system prompt",
                ]
            ),
            "MISSING_ROLE_BOUNDARIES": has_all(
                [
                    "you only",
                    "you cannot execute code",
                    "you cannot access databases",
                    "you cannot change personality",
                ]
            ),
        }

        filtered: list[Vulnerability] = []
        for vuln in vulnerabilities:
            key = vuln.vuln_type.upper()
            if key in presence and presence[key]:
                # Control is explicitly present; treat missing-* finding as false positive
                continue
            filtered.append(vuln)

        return filtered

    def _parse_llm_response(
        self,
        response: str,
        prompt: DetectedPrompt,
    ) -> list[Vulnerability]:
        """Parse LLM response to extract vulnerabilities."""
        vulnerabilities = []

        # Try to extract JSON from response
        try:
            # Look for JSON in code block first (```json ... ```)
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                # Try to find raw JSON with vulnerabilities
                json_match = re.search(r'(\{[\s\S]*"vulnerabilities"[\s\S]*\})\s*$', response)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = None
            
            if json_str:
                
                # Try to fix truncated JSON by closing brackets
                json_str = self._fix_truncated_json(json_str)
                
                data = json.loads(json_str)

                if "vulnerabilities" in data:
                    for vuln_data in data["vulnerabilities"]:
                        # Skip incomplete vulnerability entries
                        if not isinstance(vuln_data, dict):
                            continue
                        if not vuln_data.get("type"):
                            continue
                            
                        vuln_type = vuln_data.get("type", "LLM_FINDING")
                        location = vuln_data.get("location", prompt.location_str)
                        code = vuln_data.get("vulnerable_code", prompt.short_content)

                        # Use proper fingerprinting
                        vuln_id = create_fingerprint_from_parts(
                            vuln_type=vuln_type,
                            location=location,
                            code=code
                        )

                        # Parse severity safely
                        severity_str = vuln_data.get("severity", "MEDIUM")
                        try:
                            severity = VulnerabilitySeverity(severity_str.upper())
                        except ValueError:
                            severity = VulnerabilitySeverity.MEDIUM

                        vuln = Vulnerability(
                            vuln_id=vuln_id,
                            vuln_type=vuln_type,
                            severity=severity,
                            owasp_category=self._parse_owasp(vuln_data.get("owasp")),
                            location=location,
                            vulnerable_code=code,
                            description=vuln_data.get("description", ""),
                            fix=vuln_data.get("fix", ""),
                            confidence=0.8,  # LLM findings have good but not perfect confidence
                            # Extended fields for prompt quality suggestions
                            suggestion=vuln_data.get("suggestion"),
                            reasoning=vuln_data.get("reasoning"),
                            priority=vuln_data.get("priority"),
                        )
                        vulnerabilities.append(vuln)
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            # Could not parse as JSON - this is logged but not shown to user
            pass

        return vulnerabilities

    def _fix_truncated_json(self, json_str: str) -> str:
        """Attempt to fix truncated JSON by closing brackets."""
        # Count open/close brackets
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        open_brackets = json_str.count('[')
        close_brackets = json_str.count(']')
        
        # If we have unclosed structures, try to close them
        if open_braces > close_braces or open_brackets > close_brackets:
            # Remove any trailing incomplete content after last complete entry
            # Look for last complete vulnerability object
            last_complete = json_str.rfind('},')
            if last_complete > 0:
                # Find the vulnerabilities array start
                vuln_start = json_str.find('"vulnerabilities"')
                if vuln_start > 0 and last_complete > vuln_start:
                    # Truncate to last complete entry and close properly
                    json_str = json_str[:last_complete + 1] + ']}'
        
        return json_str

    def _parse_owasp(self, owasp_str: Optional[str]) -> Optional[OWASPCategory]:
        """Parse OWASP category from string."""
        if not owasp_str:
            return None

        # Extract code (LLM01, LLM02, etc.)
        match = re.search(r'LLM(\d{2})', owasp_str.upper())
        if match:
            code = f"LLM{match.group(1)}"
            names = {
                "LLM01": "Prompt Injection",
                "LLM02": "Insecure Output Handling",
                "LLM03": "Training Data Poisoning",
                "LLM04": "Model Denial of Service",
                "LLM05": "Supply Chain Vulnerabilities",
                "LLM06": "Sensitive Information Disclosure",
                "LLM07": "Insecure Plugin Design",
                "LLM08": "Excessive Agency",
                "LLM09": "Overreliance",
                "LLM10": "Model Theft",
            }
            if code in names:
                return OWASPCategory(f"{code}: {names[code]}")

        return None

    def _similarity_to_severity(self, similarity: float) -> VulnerabilitySeverity:
        """Convert similarity score to severity level."""
        if similarity >= 0.9:
            return VulnerabilitySeverity.HIGH
        elif similarity >= 0.8:
            return VulnerabilitySeverity.MEDIUM
        else:
            return VulnerabilitySeverity.LOW

    def _calculate_overall_score(self, vulnerabilities: list[Vulnerability]) -> int:
        """
        Calculate overall SECURITY score (0-100).

        Uses central scoring module for consistency across all PromptSentry components.
        See promptsentry.core.scoring for detailed documentation.

        Returns:
            Security score (0-100, where 100 = perfect security)
        """
        from promptsentry.core.scoring import calculate_security_score
        return calculate_security_score(vulnerabilities)

    def analyze_without_llm(
        self,
        prompt: DetectedPrompt,
        pattern_matches: list[PatternMatch],
        similar_matches: list[SimilarMatch],
    ) -> AnalysisResult:
        """
        Analyze without LLM (faster, for quick checks).

        Args:
            prompt: The detected prompt
            pattern_matches: Pattern matching findings
            similar_matches: Vector similarity findings

        Returns:
            Analysis result without LLM enhancement
        """
        old_use_llm = self.use_llm
        self.use_llm = False
        result = self.analyze(prompt, pattern_matches, similar_matches)
        self.use_llm = old_use_llm
        return result
