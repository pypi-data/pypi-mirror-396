"""Git pre-commit hook implementation."""

import stat
from pathlib import Path
from typing import Optional

from promptsentry.core.analyzer import PromptAnalyzer
from promptsentry.core.detector import PromptDetector
from promptsentry.core.patterns import PatternMatcher
from promptsentry.git.staged_files import get_repo_root, get_staged_files
from promptsentry.models.config import PromptSentryConfig
from promptsentry.tracker.differential import DifferentialValidator, ValidationResult
from promptsentry.utils.formatting import (
    console,
    print_commit_allowed,
    print_commit_blocked,
    print_error,
    print_success,
    print_warning,
)

import sys

def get_hook_script() -> str:
    """Generate the pre-commit hook script with the current Python interpreter."""
    python_path = sys.executable
    return f'''#!/bin/sh
# PromptSentry pre-commit hook
# Automatically scans staged files for AI prompt vulnerabilities

# Use the Python that has promptsentry installed
PYTHON="{python_path}"

# Run PromptSentry using Python directly
"$PYTHON" -m promptsentry scan --staged --hook
exit_code=$?

# If PromptSentry blocked the commit, exit with non-zero
if [ $exit_code -ne 0 ]; then
    exit $exit_code
fi

exit 0
'''


class PreCommitHook:
    """Pre-commit hook that scans staged files for vulnerabilities."""

    def __init__(
        self,
        config: Optional[PromptSentryConfig] = None,
        use_llm: bool = True,
    ):
        self.config = config or PromptSentryConfig.load()
        self.use_llm = use_llm
        self.detector = PromptDetector(min_confidence=self.config.scan.min_confidence)
        self.pattern_matcher = PatternMatcher()
        self.analyzer = None
        self.validator = DifferentialValidator(threshold=self.config.scan.threshold)

    def run(self, repo_path: Optional[Path] = None) -> int:
        if repo_path is None:
            repo_path = get_repo_root()
        if not repo_path:
            print_error("Not in a git repository")
            return 1

        staged_files = get_staged_files(repo_path)
        if not staged_files:
            print_success("No staged files to scan")
            return 0

        scannable = self._filter_scannable(staged_files, repo_path)
        if not scannable:
            print_success("No scannable files in staged changes")
            return 0

        console.print(f"[bold cyan]🔍 PromptSentry[/] Scanning {len(scannable)} file(s)...")
        console.print()

        blocked_files = []
        allowed_files = []

        for file_path in scannable:
            try:
                result, diff, message = self._scan_file(str(repo_path / file_path))
                if result == ValidationResult.BLOCK:
                    blocked_files.append((file_path, diff, message))
                else:
                    allowed_files.append((file_path, message))
            except Exception as e:
                console.print(f"[red]Error scanning {file_path}: {str(e)}[/]")
                blocked_files.append((file_path, None, f"Scan error: {str(e)}"))

        if blocked_files:
            console.print()
            for file_path, diff, message in blocked_files:
                console.print(f"[red]📁 {file_path}[/]")
                if diff is None:
                    print_commit_blocked(diff, error_message=message)
                else:
                    print_commit_blocked(diff)
            return 1

        if allowed_files:
            fixed_count = sum(1 for _, msg in allowed_files if "resolved" in msg.lower() or "fixed" in msg.lower())
            if fixed_count > 0:
                print_commit_allowed()
            else:
                print_success("All security checks passed")

        return 0

    def _filter_scannable(self, files: list[str], repo_path: Path) -> list[str]:
        scannable = []
        for file_path in files:
            ext = Path(file_path).suffix.lower()
            if ext in self.config.scan.file_extensions:
                full_path = repo_path / file_path
                if full_path.exists():
                    size = full_path.stat().st_size
                    if size <= self.config.scan.max_file_size:
                        scannable.append(file_path)
        return scannable

    def _scan_file(self, file_path: str) -> tuple[ValidationResult, any, str]:
        prompts = self.detector.detect_prompts(file_path)
        if not prompts:
            return (ValidationResult.ALLOW, None, "No prompts detected")

        all_vulnerabilities = []
        for prompt in prompts:
            pattern_matches = self.pattern_matcher.check_patterns(prompt)
            if self.analyzer is None:
                self.analyzer = PromptAnalyzer(config=self.config.llm, use_llm=self.use_llm)
            result = self.analyzer.analyze(prompt, pattern_matches)
            all_vulnerabilities.extend(result.vulnerabilities)

        from promptsentry.models.vulnerability import AnalysisResult
        from promptsentry.core.scoring import calculate_security_score
        overall_score = calculate_security_score(all_vulnerabilities)

        combined_result = AnalysisResult(
            file_path=file_path,
            prompt_location=prompts[0].location_str if prompts else "",
            vulnerabilities=all_vulnerabilities,
            overall_score=overall_score,
            is_vulnerable=len(all_vulnerabilities) > 0,
            pattern_matches=[],
            similar_matches=[],
        )
        return self.validator.validate(file_path, combined_result)


def install_hook(repo_path: Optional[Path] = None, force: bool = False) -> bool:
    if repo_path is None:
        repo_path = get_repo_root()
    if not repo_path:
        print_error("Not in a git repository")
        return False

    import subprocess
    try:
        result = subprocess.run(["git", "config", "core.hooksPath"], cwd=repo_path, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            subprocess.run(["git", "config", "--local", "core.hooksPath", ".git/hooks"], cwd=repo_path, check=True)
            console.print(f"[dim]Detected global hooks path, configured local hooks[/]")
    except Exception:
        pass

    hooks_dir = repo_path / ".git" / "hooks"
    hook_path = hooks_dir / "pre-commit"

    if hook_path.exists() and not force:
        print_warning("Pre-commit hook already exists. Use --force to overwrite.")
        return False

    try:
        hook_path.write_text(get_hook_script())
        hook_path.chmod(hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print_success(f"Pre-commit hook installed at {hook_path}")
        return True
    except Exception as e:
        print_error(f"Failed to install hook: {e}")
        return False


def uninstall_hook(repo_path: Optional[Path] = None) -> bool:
    if repo_path is None:
        repo_path = get_repo_root()
    if not repo_path:
        print_error("Not in a git repository")
        return False

    hook_path = repo_path / ".git" / "hooks" / "pre-commit"
    if not hook_path.exists():
        print_warning("No pre-commit hook found")
        return False

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
