"""
Issue Fingerprinting

Creates stable, unique identifiers for vulnerabilities that survive code refactoring.
This is a key innovation enabling differential validation.
"""

import hashlib
import re
from typing import Optional

from promptsentry.models.vulnerability import Vulnerability


def create_fingerprint(vuln: Vulnerability) -> str:
    """
    Create a stable fingerprint for a vulnerability.

    The fingerprint is based on:
    - Vulnerability type
    - Approximate location
    - Normalized vulnerable code pattern

    This allows tracking issues across minor code changes.

    Args:
        vuln: The vulnerability to fingerprint

    Returns:
        Stable fingerprint string (e.g., "VULN_DIRECT_CONCAT_a3f2b891")
    """
    # Normalize the vulnerable code for consistent hashing
    normalized_code = normalize_code(vuln.vulnerable_code)

    # Extract key location info (file + approximate line range)
    location = _normalize_location(vuln.location)

    # Create fingerprint input
    fingerprint_input = f"{vuln.vuln_type}:{location}:{normalized_code[:100]}"

    # Generate hash
    hash_id = hashlib.sha256(fingerprint_input.encode()).hexdigest()[:8]

    return f"VULN_{vuln.vuln_type}_{hash_id}"


def create_fingerprint_from_parts(
    vuln_type: str,
    location: str,
    code: str,
) -> str:
    """
    Create a fingerprint from individual components.

    Args:
        vuln_type: Type of vulnerability
        location: Location string
        code: Vulnerable code snippet

    Returns:
        Stable fingerprint string
    """
    normalized_code = normalize_code(code)
    normalized_loc = _normalize_location(location)

    fingerprint_input = f"{vuln_type}:{normalized_loc}:{normalized_code[:100]}"
    hash_id = hashlib.sha256(fingerprint_input.encode()).hexdigest()[:8]

    return f"VULN_{vuln_type}_{hash_id}"


def normalize_code(code: str) -> str:
    """
    Normalize code for consistent fingerprinting.

    Normalization:
    - Removes leading/trailing whitespace
    - Normalizes line endings
    - Collapses multiple whitespace
    - Removes variable names (keeps structure)

    Args:
        code: Raw code snippet

    Returns:
        Normalized code string
    """
    if not code:
        return ""

    # Strip whitespace
    code = code.strip()

    # Normalize line endings
    code = code.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse multiple spaces/tabs
    code = re.sub(r"[ \t]+", " ", code)

    # Collapse multiple newlines
    code = re.sub(r"\n+", "\n", code)

    # Remove common variable name variations (but keep structure)
    # Replace variable-like patterns with placeholder
    code = re.sub(r'\b[a-z_][a-z0-9_]*\s*=', "VAR=", code, flags=re.IGNORECASE)

    # Lowercase for consistency
    code = code.lower()

    return code


def _normalize_location(location: str) -> str:
    """
    Normalize location for fingerprinting.

    Groups line numbers into ranges (e.g., lines 10-19 → "lines_10")
    to survive minor line shifts.

    Args:
        location: Location string (e.g., "file.py:15")

    Returns:
        Normalized location string
    """
    if not location:
        return "unknown"

    # Extract file and line number
    match = re.match(r"([^:]+):(\d+)", location)
    if match:
        file_path = match.group(1)
        line_num = int(match.group(2))

        # Group into ranges of 10 lines
        line_group = (line_num // 10) * 10

        # Get just the filename, not full path
        file_name = file_path.split("/")[-1].split("\\")[-1]

        return f"{file_name}:lines_{line_group}"

    # If no line number, just use the location as-is
    return location.split("/")[-1].split("\\")[-1]


def fingerprints_match(fp1: str, fp2: str) -> bool:
    """
    Check if two fingerprints refer to the same issue.

    Args:
        fp1: First fingerprint
        fp2: Second fingerprint

    Returns:
        True if they match
    """
    return fp1 == fp2


def extract_vuln_type(fingerprint: str) -> Optional[str]:
    """
    Extract the vulnerability type from a fingerprint.

    Args:
        fingerprint: Fingerprint string (e.g., "VULN_DIRECT_CONCAT_a3f2b891")

    Returns:
        Vulnerability type or None
    """
    if not fingerprint.startswith("VULN_"):
        return None

    # Remove prefix and hash suffix
    parts = fingerprint[5:].rsplit("_", 1)
    if len(parts) >= 1:
        return parts[0]

    return None
