"""Git pre-commit hook implementation."""

import os
import sys
import stat
from pathlib import Path
from typing import List, Optional, Tuple

from promptsentry.git.staged_files import get_staged_files, get_repo_root, is_git_repository
from promptsentry.core.detector import PromptDetector
from promptsentry.core.patterns import PatternMatcher
# VectorDatabase removed - using rules-based SLM analysis instead
from promptsentry.core.analyzer import PromptAnalyzer
from promptsentry.tracker.differential import DifferentialValidator, ValidationResult
from promptsentry.models.config import PromptSentryConfig
from promptsentry.utils.formatting import (
    console,
    print_banner,
    print_success,
    print_error,
    print_warning,
    print_commit_blocked,
    print_commit_allowed,
    print_step,
    create_spinner,
)


# Pre-commit hook script template
HOOK_SCRIPT = '''#!/bin/sh
# PromptSentry pre-commit hook
# Automatically scans staged files for AI prompt vulnerabilities

# Run PromptSentry
promptsentry scan --staged --hook

# Capture exit code
exit_code=$?

# If PromptSentry blocked the commit, exit with non-zero
if [ $exit_code -ne 0 ]; then
    exit $exit_code
fi

exit 0
'''


class PreCommitHook:
    """
    Pre-commit hook that scans staged files for vulnerabilities.

    Implements the PromptSentry 3-stage pipeline:
    1. Get staged files and detect prompts in each file
    2. Run pattern matching with regex-based OWASP rules
    3. Analyze with SLM (Ollama + OWASP rules as context)
    4. Perform differential validation
    5. Block or allow commit based on findings
    """
    
    def __init__(
        self,
        config: Optional[PromptSentryConfig] = None,
        use_llm: bool = True,  # Enabled by default
    ):
        """
        Initialize the pre-commit hook.
        
        Args:
            config: PromptSentry configuration
            use_llm: Whether to use LLM analysis (enabled by default)
        """
        self.config = config or PromptSentryConfig.load()
        self.use_llm = use_llm
        
        # Initialize pipeline components
        self.detector = PromptDetector(
            min_confidence=self.config.scan.min_confidence
        )
        self.pattern_matcher = PatternMatcher()
        self.analyzer = None  # Lazy initialization
        self.validator = DifferentialValidator()
    
    def run(self, repo_path: Optional[Path] = None) -> int:
        """
        Run the pre-commit hook.
        
        Args:
            repo_path: Optional repository path
            
        Returns:
            Exit code (0 = allow, 1 = block)
        """
        # Get repo root
        if repo_path is None:
            repo_path = get_repo_root()
        
        if not repo_path:
            print_error("Not in a git repository")
            return 1
        
        # Get staged files
        staged_files = get_staged_files(repo_path)
        
        if not staged_files:
            print_success("No staged files to scan")
            return 0
        
        # Filter to scannable files
        scannable = self._filter_scannable(staged_files, repo_path)
        
        if not scannable:
            print_success("No scannable files in staged changes")
            return 0
        
        console.print(f"[bold cyan]🔍 PromptSentry[/] Scanning {len(scannable)} file(s)...")
        console.print()
        
        # Scan each file
        blocked_files = []
        allowed_files = []
        
        for file_path in scannable:
            full_path = repo_path / file_path
            result, diff, message = self._scan_file(str(full_path))
            
            if result == ValidationResult.BLOCK:
                blocked_files.append((file_path, diff, message))
            else:
                allowed_files.append((file_path, message))
        
        # Show results
        if blocked_files:
            console.print()
            for file_path, diff, message in blocked_files:
                console.print(f"[red]📁 {file_path}[/]")
                print_commit_blocked(diff)
            
            return 1
        
        # All passed
        if allowed_files:
            fixed_count = sum(
                1 for _, msg in allowed_files 
                if "resolved" in msg.lower() or "fixed" in msg.lower()
            )
            if fixed_count > 0:
                print_commit_allowed()
            else:
                print_success("All security checks passed")
        
        return 0
    
    def _filter_scannable(self, files: List[str], repo_path: Path) -> List[str]:
        """Filter to scannable file types."""
        scannable = []
        
        for file_path in files:
            # Check extension
            ext = Path(file_path).suffix.lower()
            if ext in self.config.scan.file_extensions:
                # Check if file exists and is not too large
                full_path = repo_path / file_path
                if full_path.exists():
                    size = full_path.stat().st_size
                    if size <= self.config.scan.max_file_size:
                        scannable.append(file_path)
        
        return scannable
    
    def _scan_file(self, file_path: str) -> Tuple[ValidationResult, any, str]:
        """Scan a single file through the pipeline."""
        # Stage 1: Detect prompts
        prompts = self.detector.detect_prompts(file_path)
        
        if not prompts:
            return (ValidationResult.ALLOW, None, "No prompts detected")
        
        # Process each prompt
        all_vulnerabilities = []
        
        for prompt in prompts:
            # Stage 2: Pattern matching
            pattern_matches = self.pattern_matcher.check_patterns(prompt)

            # Stage 3: SLM Analyzer with OWASP rules (lazy init)
            if self.analyzer is None:
                self.analyzer = PromptAnalyzer(
                    config=self.config.llm,
                    use_llm=self.use_llm,
                )

            result = self.analyzer.analyze(prompt, pattern_matches)
            all_vulnerabilities.extend(result.vulnerabilities)
        
        # Create combined result for validation
        from promptsentry.models.vulnerability import AnalysisResult
        combined_result = AnalysisResult(
            file_path=file_path,
            prompt_location=prompts[0].location_str if prompts else "",
            vulnerabilities=all_vulnerabilities,
            overall_score=max((v.severity.score for v in all_vulnerabilities), default=0),
            is_vulnerable=len(all_vulnerabilities) > 0,
            pattern_matches=[],
            similar_matches=[],
        )
        
        # Differential validation
        return self.validator.validate(file_path, combined_result)


def install_hook(repo_path: Optional[Path] = None, force: bool = False) -> bool:
    """
    Install the pre-commit hook in a git repository.
    
    Args:
        repo_path: Path to the repository
        force: Overwrite existing hook if present
        
    Returns:
        True if installed successfully
    """
    if repo_path is None:
        repo_path = get_repo_root()
    
    if not repo_path:
        print_error("Not in a git repository")
        return False
    
    hooks_dir = repo_path / ".git" / "hooks"
    hook_path = hooks_dir / "pre-commit"
    
    # Check if hook already exists
    if hook_path.exists() and not force:
        print_warning("Pre-commit hook already exists. Use --force to overwrite.")
        return False
    
    # Write hook script
    try:
        hook_path.write_text(HOOK_SCRIPT)
        
        # Make executable
        hook_path.chmod(hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        print_success(f"Pre-commit hook installed at {hook_path}")
        return True
        
    except Exception as e:
        print_error(f"Failed to install hook: {e}")
        return False


def uninstall_hook(repo_path: Optional[Path] = None) -> bool:
    """
    Uninstall the pre-commit hook.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        True if uninstalled successfully
    """
    if repo_path is None:
        repo_path = get_repo_root()
    
    if not repo_path:
        print_error("Not in a git repository")
        return False
    
    hook_path = repo_path / ".git" / "hooks" / "pre-commit"
    
    if not hook_path.exists():
        print_warning("No pre-commit hook found")
        return False
    
    # Check if it's our hook
    content = hook_path.read_text()
    if "PromptSentry" not in content:
        print_warning("Pre-commit hook is not a PromptSentry hook. Not removing.")
        return False
    
    try:
        hook_path.unlink()
        print_success("Pre-commit hook uninstalled")
        return True
        
    except Exception as e:
        print_error(f"Failed to uninstall hook: {e}")
        return False
