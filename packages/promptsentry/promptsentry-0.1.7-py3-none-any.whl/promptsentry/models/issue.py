"""Issue tracking models for PromptSentry."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from promptsentry.models.vulnerability import OWASPCategory, VulnerabilitySeverity


class IssueStatus(str, Enum):
    """Status of a tracked issue."""

    OPEN = "open"
    FIXED = "fixed"
    IGNORED = "ignored"
    FALSE_POSITIVE = "false_positive"


class Issue(BaseModel):
    """A tracked security issue."""

    issue_id: str = Field(..., description="Unique issue fingerprint")
    vuln_type: str = Field(..., description="Type of vulnerability")
    severity: VulnerabilitySeverity = Field(..., description="Severity level")
    owasp_category: Optional[OWASPCategory] = Field(None, description="OWASP category")
    location: str = Field(..., description="Location in code")
    vulnerable_code: str = Field(..., description="The vulnerable code")
    description: str = Field(..., description="Description of the issue")
    fix: str = Field(..., description="Recommended fix")
    first_seen: datetime = Field(
        default_factory=datetime.now,
        description="When the issue was first detected"
    )
    last_seen: datetime = Field(
        default_factory=datetime.now,
        description="When the issue was last detected"
    )
    status: IssueStatus = Field(IssueStatus.OPEN, description="Current status")

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "issue_id": self.issue_id,
            "vuln_type": self.vuln_type,
            "severity": self.severity.value,
            "owasp_category": self.owasp_category.value if self.owasp_category else None,
            "location": self.location,
            "vulnerable_code": self.vulnerable_code,
            "description": self.description,
            "fix": self.fix,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Issue":
        """Create from dictionary."""
        return cls(
            issue_id=data["issue_id"],
            vuln_type=data["vuln_type"],
            severity=VulnerabilitySeverity(data["severity"]),
            owasp_category=OWASPCategory(data["owasp_category"]) if data.get("owasp_category") else None,
            location=data["location"],
            vulnerable_code=data["vulnerable_code"],
            description=data["description"],
            fix=data["fix"],
            first_seen=datetime.fromisoformat(data["first_seen"]),
            last_seen=datetime.fromisoformat(data["last_seen"]),
            status=IssueStatus(data["status"]),
        )


class TrackedFile(BaseModel):
    """A file being tracked for issues."""

    file_path: str = Field(..., description="Path to the file")
    content_hash: str = Field(..., description="Hash of file content")
    last_scan: datetime = Field(
        default_factory=datetime.now,
        description="When the file was last scanned"
    )
    issues: list[Issue] = Field(default_factory=list, description="Issues found in this file")
    overall_score: int = Field(0, ge=0, le=100, description="Overall vulnerability score")

    @property
    def open_issues(self) -> list[Issue]:
        """Get only open issues."""
        return [i for i in self.issues if i.status == IssueStatus.OPEN]

    @property
    def has_open_issues(self) -> bool:
        """Check if there are open issues."""
        return len(self.open_issues) > 0

    @property
    def issue_ids(self) -> set:
        """Get set of issue IDs."""
        return {i.issue_id for i in self.issues}


class DiffResult(BaseModel):
    """Result of comparing old and new issues."""

    fixed: list[Issue] = Field(default_factory=list, description="Issues that were fixed")
    still_present: list[Issue] = Field(default_factory=list, description="Issues still present")
    new_issues: list[Issue] = Field(default_factory=list, description="New issues found")

    @property
    def is_improved(self) -> bool:
        """Check if the situation improved."""
        return len(self.fixed) > 0 and len(self.still_present) == 0

    @property
    def is_blocked(self) -> bool:
        """Check if commit should be blocked."""
        return len(self.still_present) > 0

    @property
    def summary(self) -> str:
        """Human-readable summary."""
        parts = []
        if self.fixed:
            parts.append(f"✅ Fixed: {len(self.fixed)}")
        if self.still_present:
            parts.append(f"⚠️ Remaining: {len(self.still_present)}")
        if self.new_issues:
            parts.append(f"🆕 New: {len(self.new_issues)}")
        return " | ".join(parts) if parts else "No issues"
