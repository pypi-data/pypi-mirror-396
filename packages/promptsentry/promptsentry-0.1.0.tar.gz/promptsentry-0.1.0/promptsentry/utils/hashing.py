"""Hashing utilities for PromptSentry."""

import hashlib
from pathlib import Path
from typing import Union


def content_hash(content: Union[str, bytes]) -> str:
    """
    Generate a SHA-256 hash of content.
    
    Args:
        content: String or bytes to hash
        
    Returns:
        Hex-encoded hash string
    """
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def file_hash(file_path: Union[str, Path]) -> str:
    """
    Generate a SHA-256 hash of a file's contents.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Hex-encoded hash string
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    hasher = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        # Read in chunks for large files
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    
    return hasher.hexdigest()


def short_hash(content: str, length: int = 8) -> str:
    """
    Generate a short hash for fingerprinting.
    
    Args:
        content: String to hash
        length: Length of the short hash (default 8)
        
    Returns:
        Short hex-encoded hash
    """
    return content_hash(content)[:length]


def normalize_for_hash(code: str) -> str:
    """
    Normalize code for consistent hashing.
    
    This helps create stable fingerprints that survive minor refactoring.
    
    Args:
        code: Code string to normalize
        
    Returns:
        Normalized code string
    """
    # Remove leading/trailing whitespace
    code = code.strip()
    
    # Normalize line endings
    code = code.replace("\r\n", "\n").replace("\r", "\n")
    
    # Collapse multiple spaces/tabs to single space
    import re
    code = re.sub(r"[ \t]+", " ", code)
    
    # Collapse multiple newlines to single
    code = re.sub(r"\n+", "\n", code)
    
    return code
