"""
Differential Validation

The key innovation: only block commits for previously identified issues that haven't been fixed.
This prevents "moving goalposts" where the LLM finds new nitpicks each time.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from promptsentry.models.issue import DiffResult, Issue, IssueStatus, TrackedFile
from promptsentry.models.vulnerability import AnalysisResult, Vulnerability
from promptsentry.tracker.database import IssueDatabase
from promptsentry.tracker.fingerprint import create_fingerprint
from promptsentry.utils.hashing import file_hash


class ValidationResult(Enum):
    """Result of differential validation."""

    ALLOW = "allow"  # Commit is allowed
    BLOCK = "block"  # Commit is blocked
    FIRST_SCAN = "first_scan"  # First time scanning this file


class DifferentialValidator:
    """
    Validates commits by comparing current issues with previously tracked ones.

    Key behaviors:
    1. First scan: Track all new issues, block if score >= threshold
    2. Subsequent scans: Only block if PREVIOUSLY IDENTIFIED issues still exist AND score >= threshold
    3. Fixed issues: Mark as fixed and allow commit
    4. New issues in already-scanned files: Track but don't block immediately (moving goalpost prevention)

    Threshold-based blocking (INVERTED SCORING):
    - Score is a SECURITY score (100 = perfect, 0 = terrible)
    - Default threshold: 50 (minimum acceptable security score)
    - Only blocks when score < threshold (below minimum security level)
    """

    def __init__(self, db: Optional[IssueDatabase] = None, threshold: int = 50):
        """
        Initialize the validator.

        Args:
            db: Issue database instance
            threshold: Score threshold for blocking commits (0-100)
        """
        self.db = db or IssueDatabase()
        self.threshold = threshold

    def validate(
        self,
        file_path: str,
        current_result: AnalysisResult,
    ) -> tuple[ValidationResult, DiffResult, str]:
        """
        Validate a file against its previous scan.

        Args:
            file_path: Path to the file
            current_result: Current analysis result

        Returns:
            Tuple of (result, diff, message)
        """
        # Ensure database is initialized
        self.db.initialize()

        # Get current file hash
        try:
            current_hash = file_hash(file_path)
        except FileNotFoundError:
            return (
                ValidationResult.ALLOW,
                DiffResult(),
                "File not found, skipping validation",
            )

        # Get cached tracking info
        cached = self.db.get_tracked_file(file_path)

        # Convert current vulnerabilities to issues
        current_issues = self._vulns_to_issues(current_result.vulnerabilities)
        current_issue_ids = {i.issue_id for i in current_issues}

        # First time seeing this file?
        if not cached:
            return self._handle_first_scan(
                file_path, current_hash, current_issues, current_result
            )

        # File was scanned before - perform differential validation
        return self._handle_differential(
            file_path, current_hash, cached, current_issues, current_issue_ids
        )

    def _handle_first_scan(
        self,
        file_path: str,
        content_hash: str,
        current_issues: list[Issue],
        result: AnalysisResult,
    ) -> tuple[ValidationResult, DiffResult, str]:
        """Handle first scan of a file."""
        if current_issues:
            # Save issues for future tracking
            tracked = TrackedFile(
                file_path=file_path,
                content_hash=content_hash,
                last_scan=datetime.now(),
                issues=current_issues,
                overall_score=result.overall_score,
            )
            self.db.save_tracked_file(tracked)
            self.db.save_issues(current_issues, file_path)

            diff = DiffResult(
                fixed=[],
                still_present=current_issues,
                new_issues=[],
            )

            issues_text = ", ".join(i.vuln_type for i in current_issues[:3])
            if len(current_issues) > 3:
                issues_text += f" (+{len(current_issues) - 3} more)"

            # Check threshold - block if security score is too LOW (INVERTED)
            if result.overall_score < self.threshold:
                return (
                    ValidationResult.BLOCK,
                    diff,
                    f"Found {len(current_issues)} issue(s) with security score {result.overall_score}/100 (minimum: {self.threshold})",
                )
            else:
                return (
                    ValidationResult.ALLOW,
                    diff,
                    f"Issues tracked but security score {result.overall_score}/100 meets minimum {self.threshold}",
                )

        # No issues found on first scan
        tracked = TrackedFile(
            file_path=file_path,
            content_hash=content_hash,
            last_scan=datetime.now(),
            issues=[],
            overall_score=0,
        )
        self.db.save_tracked_file(tracked)

        return (
            ValidationResult.ALLOW,
            DiffResult(),
            "No vulnerabilities detected",
        )

    def _handle_differential(
        self,
        file_path: str,
        current_hash: str,
        cached: TrackedFile,
        current_issues: list[Issue],
        current_issue_ids: set,
    ) -> tuple[ValidationResult, DiffResult, str]:
        """Handle differential validation for previously scanned file."""

        # Get previously tracked open issues
        old_issues = {i.issue_id: i for i in cached.issues if i.status == IssueStatus.OPEN}
        old_issue_ids = set(old_issues.keys())

        # Calculate diff
        fixed = []
        still_present = []
        new_issues = []

        for issue_id, issue in old_issues.items():
            if issue_id in current_issue_ids:
                # Issue still present
                still_present.append(issue)
            else:
                # Issue no longer detected = fixed!
                fixed.append(issue)

        for issue in current_issues:
            if issue.issue_id not in old_issue_ids:
                # New issue found
                new_issues.append(issue)

        diff = DiffResult(
            fixed=fixed,
            still_present=still_present,
            new_issues=new_issues,
        )

        # Update database
        self._update_database(file_path, current_hash, diff, current_issues)

        # Decision logic (INVERTED SCORING)
        if still_present:
            # Calculate current SECURITY score using central scoring module
            from promptsentry.core.scoring import calculate_security_score
            current_score = calculate_security_score(current_issues)

            # Block if security score is below threshold
            if current_score < self.threshold:
                message = f"{len(still_present)} issue(s) remain, security score {current_score}/100 (minimum: {self.threshold})"
                if fixed:
                    message += f", {len(fixed)} fixed"
                return (ValidationResult.BLOCK, diff, message)
            else:
                # Security score acceptable - allow but warn
                message = f"{len(still_present)} issue(s) remain but security score {current_score}/100 meets minimum"
                if fixed:
                    message += f", {len(fixed)} fixed"
                return (ValidationResult.ALLOW, diff, message)

        if fixed:
            # All tracked issues fixed!
            return (
                ValidationResult.ALLOW,
                diff,
                f"All {len(fixed)} issue(s) resolved!",
            )

        if new_issues:
            # New issues found, but no tracked issues blocking
            # Track them but allow commit (don't move goalposts)
            return (
                ValidationResult.ALLOW,
                diff,
                f"Commit allowed. Note: {len(new_issues)} new issue(s) detected for next scan.",
            )

        # No issues at all
        return (
            ValidationResult.ALLOW,
            diff,
            "All checks passed",
        )

    def _update_database(
        self,
        file_path: str,
        content_hash: str,
        diff: DiffResult,
        current_issues: list[Issue],
    ) -> None:
        """Update database with validation results."""
        now = datetime.now()

        # If the file is now clean, clear any previously tracked issues to avoid
        # stale blocks in future commits. We still persist the tracked file with
        # an updated hash/score so differential validation remains fast.
        if not current_issues:
            self.db.clear_issues_for_file(file_path)
            from promptsentry.core.scoring import calculate_security_score
            score = calculate_security_score(current_issues)
            tracked = TrackedFile(
                file_path=file_path,
                content_hash=content_hash,
                last_scan=now,
                issues=[],
                overall_score=score,
            )
            self.db.save_tracked_file(tracked)
            return

        # Mark fixed issues
        for issue in diff.fixed:
            self.db.update_issue_status(issue.issue_id, IssueStatus.FIXED)

        # Update last_seen for still-present issues
        for issue in diff.still_present:
            issue.last_seen = now
            self.db.save_issue(issue, file_path)

        # Add new issues
        for issue in diff.new_issues:
            self.db.save_issue(issue, file_path)

        # Update tracked file
        from promptsentry.core.scoring import calculate_security_score
        score = calculate_security_score(current_issues)
        tracked = TrackedFile(
            file_path=file_path,
            content_hash=content_hash,
            last_scan=now,
            issues=current_issues,
            overall_score=score,
        )
        self.db.save_tracked_file(tracked)

    def _vulns_to_issues(self, vulns: list[Vulnerability]) -> list[Issue]:
        """Convert vulnerabilities to trackable issues."""
        issues = []
        now = datetime.now()

        for vuln in vulns:
            # Create or use existing fingerprint
            issue_id = vuln.vuln_id or create_fingerprint(vuln)

            issue = Issue(
                issue_id=issue_id,
                vuln_type=vuln.vuln_type,
                severity=vuln.severity,
                owasp_category=vuln.owasp_category,
                location=vuln.location,
                vulnerable_code=vuln.vulnerable_code,
                description=vuln.description,
                fix=vuln.fix,
                first_seen=now,
                last_seen=now,
                status=IssueStatus.OPEN,
            )
            issues.append(issue)

        return issues

    def clear_file(self, file_path: str) -> None:
        """
        Clear all tracking data for a file.

        Args:
            file_path: File to clear
        """
        self.db.delete_tracked_file(file_path)

    def ignore_issue(self, issue_id: str) -> None:
        """
        Mark an issue as ignored (won't block commits).

        Args:
            issue_id: Issue ID to ignore
        """
        self.db.update_issue_status(issue_id, IssueStatus.IGNORED)

    def get_tracked_issues(self, file_path: Optional[str] = None) -> list[Issue]:
        """
        Get tracked issues.

        Args:
            file_path: Optional file to filter by

        Returns:
            List of issues
        """
        if file_path:
            return self.db.get_issues_for_file(file_path)
        return self.db.get_all_issues()
