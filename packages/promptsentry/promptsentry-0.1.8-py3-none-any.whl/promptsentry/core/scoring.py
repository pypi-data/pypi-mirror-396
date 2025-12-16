"""
Central Security Scoring Module

Provides consistent scoring logic across all PromptSentry components.

Scoring is based on COUNT of missing controls, with severity as a weight.
This ensures:
- 0 issues = 100 (perfect)
- 1 issue = 80-90 (good, passes threshold)
- 3-4 issues = 50-60 (medium, borderline)
- 6+ issues = 20-40 (poor)
- 8+ issues = 0-20 (critical)
"""

from typing import List


# Severity weights (lower = less penalty per issue)
SEVERITY_WEIGHTS = {
    "CRITICAL": 12,
    "HIGH": 10,
    "MEDIUM": 8,
    "LOW": 5,
    "INFO": 2,
}


def calculate_security_score(vulnerabilities: List) -> int:
    """
    Calculate overall SECURITY score (0-100).

    Formula: 100 - weighted_penalty
    
    Where weighted_penalty = sum of (severity_weight for each vulnerability)
    
    Severity Weights:
    - CRITICAL: 12 points per issue
    - HIGH: 10 points per issue
    - MEDIUM: 8 points per issue
    - LOW: 5 points per issue
    - INFO: 2 points per issue

    Examples:
    - 0 issues = 100
    - 1 CRITICAL = 100 - 12 = 88 (passes 50 threshold)
    - 1 MEDIUM = 100 - 8 = 92
    - 4 CRITICAL = 100 - 48 = 52 (borderline)
    - 8 CRITICAL = 100 - 96 = 4 (fails badly)
    - 8 MEDIUM = 100 - 64 = 36 (fails)

    Args:
        vulnerabilities: List of Vulnerability or Issue objects with .severity attribute

    Returns:
        Security score (0-100, where 100 is perfect security)
    """
    if not vulnerabilities:
        return 100  # Perfect score - no vulnerabilities

    # Calculate weighted penalty based on count and severity
    total_penalty = 0
    for vuln in vulnerabilities:
        severity_name = vuln.severity.value if hasattr(vuln.severity, 'value') else str(vuln.severity)
        weight = SEVERITY_WEIGHTS.get(severity_name.upper(), 8)
        total_penalty += weight

    # Score = 100 - penalty, minimum 0
    security_score = max(100 - total_penalty, 0)
    return security_score


def calculate_penalty(vulnerabilities: List) -> int:
    """
    Calculate total penalty from vulnerabilities.

    Args:
        vulnerabilities: List of Vulnerability or Issue objects

    Returns:
        Total penalty (0-100+)
    """
    if not vulnerabilities:
        return 0

    total_penalty = 0
    for vuln in vulnerabilities:
        severity_name = vuln.severity.value if hasattr(vuln.severity, 'value') else str(vuln.severity)
        weight = SEVERITY_WEIGHTS.get(severity_name.upper(), 8)
        total_penalty += weight

    return total_penalty
