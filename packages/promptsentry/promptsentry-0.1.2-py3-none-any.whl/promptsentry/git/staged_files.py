"""Git staged files detection."""

import subprocess
from pathlib import Path
from typing import List, Optional, Tuple


def get_staged_files(repo_path: Optional[Path] = None) -> List[str]:
    """
    Get list of staged files in the git repository.
    
    Args:
        repo_path: Optional path to the repository root
        
    Returns:
        List of staged file paths (relative to repo root)
    """
    cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        
        files = result.stdout.strip().split("\n")
        return [f for f in files if f]  # Filter empty strings
        
    except subprocess.CalledProcessError:
        return []


def get_staged_content(file_path: str, repo_path: Optional[Path] = None) -> Optional[str]:
    """
    Get the staged content of a file.
    
    Args:
        file_path: Relative path to the file
        repo_path: Optional path to the repository root
        
    Returns:
        Staged content or None if not staged
    """
    cmd = ["git", "show", f":{file_path}"]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
        
    except subprocess.CalledProcessError:
        return None


def get_repo_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Get the root directory of the git repository.
    
    Args:
        start_path: Starting path for search
        
    Returns:
        Repository root path or None
    """
    cmd = ["git", "rev-parse", "--show-toplevel"]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=start_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
        
    except subprocess.CalledProcessError:
        return None


def is_git_repository(path: Optional[Path] = None) -> bool:
    """
    Check if the current directory is a git repository.
    
    Args:
        path: Path to check
        
    Returns:
        True if in a git repository
    """
    return get_repo_root(path) is not None


def get_modified_files(repo_path: Optional[Path] = None) -> List[str]:
    """
    Get list of modified (but not necessarily staged) files.
    
    Args:
        repo_path: Optional path to the repository root
        
    Returns:
        List of modified file paths
    """
    cmd = ["git", "diff", "--name-only"]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        
        files = result.stdout.strip().split("\n")
        return [f for f in files if f]
        
    except subprocess.CalledProcessError:
        return []


def get_file_diff(file_path: str, repo_path: Optional[Path] = None) -> Optional[str]:
    """
    Get the diff for a specific file.
    
    Args:
        file_path: Path to the file
        repo_path: Optional repository root
        
    Returns:
        Diff output or None
    """
    cmd = ["git", "diff", "--cached", file_path]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
        
    except subprocess.CalledProcessError:
        return None
