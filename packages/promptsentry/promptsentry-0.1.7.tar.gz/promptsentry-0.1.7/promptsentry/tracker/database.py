"""
Issue Database

SQLite-based storage for tracked issues, enabling persistent issue tracking
across commits and sessions.

Thread-safe: Uses thread-local connections for safe multi-threaded access.
"""

import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from promptsentry.models.config import DEFAULT_CONFIG_DIR
from promptsentry.models.issue import Issue, IssueStatus, TrackedFile
from promptsentry.models.vulnerability import OWASPCategory, VulnerabilitySeverity


class IssueDatabase:
    """
    SQLite database for tracking security issues across scans.

    Thread-safe: Each thread gets its own database connection via thread-local storage.

    Stores:
    - Tracked files with content hashes
    - Issues with fingerprints for differential validation
    - Scan history for debugging
    """

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS tracked_files (
        file_path TEXT PRIMARY KEY,
        content_hash TEXT NOT NULL,
        last_scan TEXT NOT NULL,
        overall_score INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS issues (
        issue_id TEXT PRIMARY KEY,
        file_path TEXT NOT NULL,
        vuln_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        owasp_category TEXT,
        location TEXT NOT NULL,
        vulnerable_code TEXT NOT NULL,
        description TEXT NOT NULL,
        fix TEXT NOT NULL,
        first_seen TEXT NOT NULL,
        last_seen TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'open',
        FOREIGN KEY (file_path) REFERENCES tracked_files(file_path)
    );

    CREATE INDEX IF NOT EXISTS idx_issues_file ON issues(file_path);
    CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status);
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the database.

        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            db_path = DEFAULT_CONFIG_DIR / "issues.db"

        self.db_path = Path(db_path)
        self._local = threading.local()  # Thread-local storage for connections
        self._schema_initialized = False
        self._lock = threading.Lock()  # Lock for schema initialization

    def initialize(self) -> None:
        """Initialize the database schema (thread-safe)."""
        # Schema initialization only needs to happen once globally
        with self._lock:
            if self._schema_initialized:
                return

            # Ensure parent directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            # Create schema using a temporary connection
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            with conn:
                conn.executescript(self.SCHEMA)
            conn.close()

            self._schema_initialized = True

    def _get_thread_connection(self) -> sqlite3.Connection:
        """Get a thread-local database connection."""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(str(self.db_path))
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection

    @property
    def connection(self) -> sqlite3.Connection:
        """Get database connection for current thread, initializing if needed."""
        if not self._schema_initialized:
            self.initialize()
        return self._get_thread_connection()

    # =========================================================================
    # File Operations
    # =========================================================================

    def get_tracked_file(self, file_path: str) -> Optional[TrackedFile]:
        """
        Get tracked file info if exists.

        Args:
            file_path: Path to the file

        Returns:
            TrackedFile if exists, None otherwise
        """
        cursor = self.connection.execute(
            "SELECT * FROM tracked_files WHERE file_path = ?",
            (file_path,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        # Get issues for this file
        issues = self.get_issues_for_file(file_path)

        return TrackedFile(
            file_path=row["file_path"],
            content_hash=row["content_hash"],
            last_scan=datetime.fromisoformat(row["last_scan"]),
            issues=issues,
            overall_score=row["overall_score"],
        )

    def save_tracked_file(self, tracked_file: TrackedFile) -> None:
        """
        Save or update tracked file.

        Args:
            tracked_file: TrackedFile to save
        """
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO tracked_files
                (file_path, content_hash, last_scan, overall_score)
                VALUES (?, ?, ?, ?)
                """,
                (
                    tracked_file.file_path,
                    tracked_file.content_hash,
                    tracked_file.last_scan.isoformat(),
                    tracked_file.overall_score,
                )
            )

    def delete_tracked_file(self, file_path: str) -> None:
        """
        Delete tracked file and its issues.

        Args:
            file_path: Path to the file
        """
        with self.connection:
            self.connection.execute(
                "DELETE FROM issues WHERE file_path = ?",
                (file_path,)
            )
            self.connection.execute(
                "DELETE FROM tracked_files WHERE file_path = ?",
                (file_path,)
            )

    # =========================================================================
    # Issue Operations
    # =========================================================================

    def get_issues_for_file(
        self,
        file_path: str,
        status: Optional[IssueStatus] = None,
    ) -> list[Issue]:
        """
        Get all issues for a file.

        Args:
            file_path: Path to the file
            status: Optional filter by status

        Returns:
            List of issues
        """
        if status:
            cursor = self.connection.execute(
                "SELECT * FROM issues WHERE file_path = ? AND status = ?",
                (file_path, status.value)
            )
        else:
            cursor = self.connection.execute(
                "SELECT * FROM issues WHERE file_path = ?",
                (file_path,)
            )

        return [self._row_to_issue(row) for row in cursor.fetchall()]

    def get_open_issues_for_file(self, file_path: str) -> list[Issue]:
        """Get only open issues for a file."""
        return self.get_issues_for_file(file_path, IssueStatus.OPEN)

    def get_all_issues(self, status: Optional[IssueStatus] = None) -> list[Issue]:
        """
        Get all tracked issues.

        Args:
            status: Optional filter by status

        Returns:
            List of all issues
        """
        if status:
            cursor = self.connection.execute(
                "SELECT * FROM issues WHERE status = ?",
                (status.value,)
            )
        else:
            cursor = self.connection.execute("SELECT * FROM issues")

        return [self._row_to_issue(row) for row in cursor.fetchall()]

    def save_issue(self, issue: Issue, file_path: str) -> None:
        """
        Save or update an issue.

        Args:
            issue: Issue to save
            file_path: File path the issue belongs to
        """
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO issues
                (issue_id, file_path, vuln_type, severity, owasp_category,
                 location, vulnerable_code, description, fix, first_seen,
                 last_seen, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    issue.issue_id,
                    file_path,
                    issue.vuln_type,
                    issue.severity.value,
                    issue.owasp_category.value if issue.owasp_category else None,
                    issue.location,
                    issue.vulnerable_code,
                    issue.description,
                    issue.fix,
                    issue.first_seen.isoformat(),
                    issue.last_seen.isoformat(),
                    issue.status.value,
                )
            )

    def save_issues(self, issues: list[Issue], file_path: str) -> None:
        """
        Save multiple issues.

        Args:
            issues: List of issues to save
            file_path: File path the issues belong to
        """
        for issue in issues:
            self.save_issue(issue, file_path)

    def update_issue_status(self, issue_id: str, status: IssueStatus) -> None:
        """
        Update the status of an issue.

        Args:
            issue_id: Issue fingerprint ID
            status: New status
        """
        with self.connection:
            self.connection.execute(
                "UPDATE issues SET status = ? WHERE issue_id = ?",
                (status.value, issue_id)
            )

    def mark_issues_fixed(self, issue_ids: list[str]) -> None:
        """
        Mark multiple issues as fixed.

        Args:
            issue_ids: List of issue IDs to mark as fixed
        """
        with self.connection:
            for issue_id in issue_ids:
                self.update_issue_status(issue_id, IssueStatus.FIXED)

    def delete_issue(self, issue_id: str) -> None:
        """
        Delete an issue.

        Args:
            issue_id: Issue ID to delete
        """
        with self.connection:
            self.connection.execute(
                "DELETE FROM issues WHERE issue_id = ?",
                (issue_id,)
            )

    def clear_issues_for_file(self, file_path: str) -> None:
        """
        Clear all issues for a file.

        Args:
            file_path: File path to clear issues for
        """
        with self.connection:
            self.connection.execute(
                "DELETE FROM issues WHERE file_path = ?",
                (file_path,)
            )

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_stats(self) -> dict[str, Any]:
        """Get database statistics."""
        cursor = self.connection.execute(
            "SELECT COUNT(*) as count FROM tracked_files"
        )
        file_count = cursor.fetchone()["count"]

        cursor = self.connection.execute(
            "SELECT status, COUNT(*) as count FROM issues GROUP BY status"
        )
        issue_counts = {row["status"]: row["count"] for row in cursor.fetchall()}

        return {
            "tracked_files": file_count,
            "issues": {
                "open": issue_counts.get("open", 0),
                "fixed": issue_counts.get("fixed", 0),
                "ignored": issue_counts.get("ignored", 0),
                "total": sum(issue_counts.values()),
            }
        }

    # =========================================================================
    # Helpers
    # =========================================================================

    def _row_to_issue(self, row: sqlite3.Row) -> Issue:
        """Convert database row to Issue object."""
        owasp = None
        if row["owasp_category"]:
            try:
                owasp = OWASPCategory(row["owasp_category"])
            except ValueError:
                pass

        return Issue(
            issue_id=row["issue_id"],
            vuln_type=row["vuln_type"],
            severity=VulnerabilitySeverity(row["severity"]),
            owasp_category=owasp,
            location=row["location"],
            vulnerable_code=row["vulnerable_code"],
            description=row["description"],
            fix=row["fix"],
            first_seen=datetime.fromisoformat(row["first_seen"]),
            last_seen=datetime.fromisoformat(row["last_seen"]),
            status=IssueStatus(row["status"]),
        )

    def close(self) -> None:
        """Close the database connection for the current thread."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
