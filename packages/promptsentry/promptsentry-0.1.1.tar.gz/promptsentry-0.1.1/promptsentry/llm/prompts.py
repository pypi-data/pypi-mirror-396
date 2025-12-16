"""LLM prompt templates for vulnerability analysis."""

from pathlib import Path
from typing import Optional


def load_owasp_rules() -> str:
    """Load OWASP LLM Top 10 2025 rules from YAML file."""
    try:
        from promptsentry.core.rules_loader import RulesLoader

        rules_loader = RulesLoader()
        rules_loader.initialize()

        # Get rules as formatted text
        rules_text = rules_loader.get_rules_as_text()
        return rules_text
    except Exception as e:
        # Fallback to basic rules if loading fails
        return """
# OWASP LLM Top 10 2025 (Fallback)

Basic vulnerability categories:
- LLM01: Prompt Injection
- LLM02: Sensitive Information Disclosure
- LLM03: Supply Chain Vulnerabilities
- LLM04: Data and Model Poisoning
- LLM05: Improper Output Handling
- LLM06: Excessive Agency
- LLM07: System Prompt Leakage
- LLM08: Vector and Embedding Weaknesses
- LLM09: Misinformation
- LLM10: Unbounded Consumption
"""


def get_judge_system_prompt() -> str:
    """
    Get the system prompt for the LLM judge with comprehensive OWASP rules.

    Returns:
        System prompt containing OWASP LLM Top 10 2025 rules
    """
    owasp_rules = load_owasp_rules()

    return f"""You are a specialized security analyst for AI prompts and LLM applications.
You are an expert in identifying vulnerabilities based on the OWASP LLM Top 10 2025.

Your expertise includes comprehensive knowledge of:

{owasp_rules}

Your task is to:
1. Analyze the provided AI prompt code for security vulnerabilities
2. Validate if preliminary findings from pattern matching are true vulnerabilities
3. Identify any additional vulnerabilities missed by automated checks
4. Provide specific, actionable findings with exact fixes
5. Consider the full context of how the code is used

IMPORTANT ANALYSIS GUIDELINES:
- Be precise and avoid false positives
- Focus on REAL, EXPLOITABLE security issues, not theoretical concerns
- Not all f-strings or concatenations are vulnerable - check if user input is involved
- Consider defense-in-depth: missing one control may not be critical if others exist
- Each finding MUST include:
  * Specific vulnerability type
  * OWASP category (LLM01-LLM10)
  * Severity level (CRITICAL, HIGH, MEDIUM, LOW)
  * Exact location (line number or function name)
  * The vulnerable code snippet
  * Clear description of why it's vulnerable
  * Specific fix to apply

OUTPUT FORMAT:
- Return valid JSON only
- Use the exact structure specified in the analysis prompt
- Set is_vulnerable=true ONLY if there are genuine security issues
- Provide clear, actionable recommendations"""


# Keep backward compatibility
JUDGE_SYSTEM_PROMPT = get_judge_system_prompt()


def create_analysis_prompt(
    detected_prompt: str,
    pattern_findings: list,
    vector_findings: list,
) -> str:
    """
    Create the analysis prompt for the LLM judge.
    
    Args:
        detected_prompt: The prompt content being analyzed
        pattern_findings: Findings from pattern matching stage
        vector_findings: Findings from vector similarity stage
        
    Returns:
        Formatted prompt for the LLM
    """
    import json
    
    context_summary = ""
    
    if pattern_findings:
        context_summary += "Pattern Analysis Found:\n"
        for finding in pattern_findings:
            context_summary += f"  - [{finding['severity']}] {finding['id']}: {finding['description']}\n"
        context_summary += "\n"
    
    if vector_findings:
        context_summary += "Similarity Analysis Found:\n"
        for finding in vector_findings:
            context_summary += f"  - [{finding['similarity']:.0%} match] {finding['vulnerability']}\n"
        context_summary += "\n"
    
    if not context_summary:
        context_summary = "No preliminary findings from pattern or similarity analysis.\n"
    
    return f"""Analyze this AI prompt for security vulnerabilities:

```
{detected_prompt[:2000]}
```

Preliminary Analysis:
{context_summary}

Provide your analysis as JSON:
{{
  "vulnerabilities": [
    {{
      "type": "VULNERABILITY_TYPE",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "owasp": "LLM01",
      "location": "specific location or line",
      "vulnerable_code": "the problematic code snippet",
      "description": "clear description of the vulnerability",
      "fix": "specific fix to apply"
    }}
  ],
  "is_vulnerable": true/false,
  "overall_score": 0-100,
  "analysis_notes": "additional context or reasoning"
}}

RULES:
- Only report genuine security vulnerabilities
- Validate pattern findings (confirm or dismiss)
- Add any vulnerabilities the patterns missed
- Be specific about fixes
- Set is_vulnerable=true only if there are real issues"""
