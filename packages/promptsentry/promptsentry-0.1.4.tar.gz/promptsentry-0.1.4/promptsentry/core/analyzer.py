"""
Stage 3: Prompt Analyzer (SLM Judge)

Final analysis using Ollama (qwen2.5-coder:0.5b) as a small language model judge.
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
            model_name = self.config.model_name or "qwen2.5-coder:0.5b"
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

        # Convert pattern matches to vulnerabilities
        for match in pattern_matches:
            # Use proper fingerprinting for stable IDs across code changes
            vuln_id = create_fingerprint_from_parts(
                vuln_type=match.pattern_id,
                location=match.location,
                code=match.matched_code
            )
            vuln = Vulnerability(
                vuln_id=vuln_id,
                vuln_type=match.pattern_id,
                severity=match.severity,
                owasp_category=match.owasp_category,
                location=match.location,
                vulnerable_code=match.matched_code,
                description=match.description,
                fix=match.fix,
                confidence=1.0,  # Pattern matches are high confidence
            )
            vulnerabilities.append(vuln)

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
        llm_analysis = None
        if self.use_llm and (pattern_matches or prompt.confidence > 0.7):
            try:
                llm_vulns, llm_analysis = self._llm_analyze(
                    prompt, pattern_matches, similar_matches
                )

                # Add LLM-discovered vulnerabilities
                for vuln in llm_vulns:
                    # Check if not already reported
                    if not any(v.vuln_type == vuln.vuln_type for v in vulnerabilities):
                        vulnerabilities.append(vuln)

            except Exception as e:
                # LLM analysis failed, continue with other findings
                llm_analysis = f"LLM analysis error: {str(e)}"

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

    def _parse_llm_response(
        self,
        response: str,
        prompt: DetectedPrompt,
    ) -> list[Vulnerability]:
        """Parse LLM response to extract vulnerabilities."""
        vulnerabilities = []

        # Try to extract JSON from response
        try:
            # Look for JSON block
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())

                if "vulnerabilities" in data:
                    for vuln_data in data["vulnerabilities"]:
                        vuln_type = vuln_data.get("type", "LLM_FINDING")
                        location = vuln_data.get("location", prompt.location_str)
                        code = vuln_data.get("vulnerable_code", prompt.short_content)

                        # Use proper fingerprinting
                        vuln_id = create_fingerprint_from_parts(
                            vuln_type=vuln_type,
                            location=location,
                            code=code
                        )

                        vuln = Vulnerability(
                            vuln_id=vuln_id,
                            vuln_type=vuln_type,
                            severity=VulnerabilitySeverity(
                                vuln_data.get("severity", "MEDIUM").upper()
                            ),
                            owasp_category=self._parse_owasp(vuln_data.get("owasp")),
                            location=location,
                            vulnerable_code=code,
                            description=vuln_data.get("description", ""),
                            fix=vuln_data.get("fix", ""),
                            confidence=0.8,  # LLM findings have good but not perfect confidence
                        )
                        vulnerabilities.append(vuln)
        except (json.JSONDecodeError, KeyError, ValueError):
            # Could not parse as JSON, try text extraction
            pass

        return vulnerabilities

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
        """Calculate overall vulnerability score (0-100)."""
        if not vulnerabilities:
            return 0

        # Weight by severity
        total_score = sum(v.severity.score * v.confidence for v in vulnerabilities)

        # Normalize to 0-100
        max_possible = len(vulnerabilities) * 100  # If all were CRITICAL
        score = int((total_score / max_possible) * 100) if max_possible > 0 else 0

        return min(score, 100)

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
