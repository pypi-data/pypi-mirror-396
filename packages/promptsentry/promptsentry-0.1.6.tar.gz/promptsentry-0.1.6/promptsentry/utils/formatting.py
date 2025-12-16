"""Rich console formatting utilities for PromptSentry CLI."""

from typing import Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from promptsentry.models.issue import DiffResult, Issue
from promptsentry.models.vulnerability import AnalysisResult, Vulnerability, VulnerabilitySeverity

# Global console instance
console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# BANNER AND BRANDING
# ═══════════════════════════════════════════════════════════════════════════════

BANNER = """
[bold cyan]╔═══════════════════════════════════════════════════════════════╗[/]
[bold cyan]║[/]  [bold white]🛡️  PromptSentry[/] - AI Prompt Security Scanner             [bold cyan]║[/]
[bold cyan]║[/]  [dim]Protect your LLM applications from prompt injection[/]      [bold cyan]║[/]
[bold cyan]╚═══════════════════════════════════════════════════════════════╝[/]
"""

MINI_BANNER = "[bold cyan]🛡️  PromptSentry[/]"


def print_banner(mini: bool = False) -> None:
    """Print the PromptSentry banner."""
    if mini:
        console.print(MINI_BANNER)
    else:
        console.print(BANNER)


# ═══════════════════════════════════════════════════════════════════════════════
# STATUS MESSAGES
# ═══════════════════════════════════════════════════════════════════════════════

def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]✅ {message}[/]")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]❌ {message}[/]")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[bold yellow]⚠️  {message}[/]")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[bold blue]ℹ️  {message}[/]")


def print_step(message: str, status: str = "working") -> None:
    """Print a step with status indicator."""
    indicators = {
        "working": "[bold cyan]→[/]",
        "done": "[bold green]✓[/]",
        "skip": "[dim]○[/]",
        "error": "[bold red]✗[/]",
    }
    ind = indicators.get(status, indicators["working"])
    console.print(f"   {ind} {message}")


# ═══════════════════════════════════════════════════════════════════════════════
# PROGRESS INDICATORS
# ═══════════════════════════════════════════════════════════════════════════════

def create_progress() -> Progress:
    """Create a progress bar for long operations."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        console=console,
    )


def create_spinner() -> Progress:
    """Create a simple spinner for indeterminate operations."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        console=console,
        transient=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# VULNERABILITY DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def format_severity(severity: VulnerabilitySeverity) -> Text:
    """Format severity with color and emoji."""
    return Text(f"{severity.emoji} {severity.value}", style=severity.color)


def print_vulnerability(vuln: Vulnerability, show_fix: bool = True) -> None:
    """Print a single vulnerability in a styled panel."""
    severity_text = format_severity(vuln.severity)

    # Build content
    content = Text()
    content.append("📍 Location: ", style="dim")
    content.append(f"{vuln.location}\n", style="cyan")
    content.append("\n")
    content.append(f"📝 {vuln.description}\n", style="white")
    content.append("\n")
    content.append("Vulnerable Code:\n", style="dim")

    # Create panel
    title = Text()
    title.append_text(severity_text)
    title.append(f" - {vuln.vuln_type}")

    panel = Panel(
        content,
        title=title,
        title_align="left",
        border_style=vuln.severity.color.split()[0],  # Get just the color
        box=box.ROUNDED,
    )
    console.print(panel)

    # Show vulnerable code with syntax highlighting
    console.print(Syntax(vuln.vulnerable_code, "python", theme="monokai", line_numbers=False))

    if show_fix and vuln.fix:
        console.print()
        console.print("[bold green]💡 Fix:[/]", vuln.fix)

    console.print()


def print_vulnerability_summary(vulns: list[Vulnerability]) -> None:
    """Print a summary table of vulnerabilities."""
    if not vulns:
        print_success("No vulnerabilities found!")
        return

    table = Table(
        title="Vulnerability Summary",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )

    table.add_column("Severity", justify="center", width=12)
    table.add_column("Type", width=25)
    table.add_column("Location", width=20)
    table.add_column("Description", width=40)

    for vuln in sorted(vulns, key=lambda v: -v.severity.score):
        table.add_row(
            format_severity(vuln.severity),
            vuln.vuln_type,
            vuln.location,
            vuln.description[:40] + "..." if len(vuln.description) > 40 else vuln.description,
        )

    console.print(table)


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS RESULTS
# ═══════════════════════════════════════════════════════════════════════════════

def print_analysis_result(result: AnalysisResult) -> None:
    """Print the complete analysis result."""
    console.print(Rule(f"[bold]Analysis: {result.file_path}[/]"))
    console.print()

    # Score display
    score_color = "green" if result.overall_score < 30 else "yellow" if result.overall_score < 70 else "red"
    console.print(f"[bold]Overall Score:[/] [{score_color}]{result.overall_score}/100[/]")
    console.print()

    if result.vulnerabilities:
        console.print(f"[bold red]❌ Found {len(result.vulnerabilities)} vulnerability(ies)[/]")
        console.print()

        for vuln in result.vulnerabilities:
            print_vulnerability(vuln)
    else:
        print_success("No vulnerabilities detected!")


def print_scan_summary(results: list[AnalysisResult]) -> None:
    """Print summary of multiple file scans."""
    total_vulns = sum(len(r.vulnerabilities) for r in results)
    total_files = len(results)
    vulnerable_files = sum(1 for r in results if r.is_vulnerable)

    console.print()
    console.print(Rule("[bold]Scan Summary[/]"))
    console.print()

    table = Table(box=box.SIMPLE)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    table.add_row("Files Scanned", str(total_files))
    table.add_row("Vulnerable Files", f"[red]{vulnerable_files}[/]" if vulnerable_files else "[green]0[/]")
    table.add_row("Total Vulnerabilities", f"[red]{total_vulns}[/]" if total_vulns else "[green]0[/]")

    console.print(table)


# ═══════════════════════════════════════════════════════════════════════════════
# DIFF RESULTS (FOR DIFFERENTIAL VALIDATION)
# ═══════════════════════════════════════════════════════════════════════════════

def print_diff_result(diff: DiffResult) -> None:
    """Print differential validation results."""
    console.print()

    if diff.fixed:
        console.print(f"[bold green]✅ Fixed Issues ({len(diff.fixed)}):[/]")
        for issue in diff.fixed:
            console.print(f"   [green]✓[/] {issue.vuln_type} at {issue.location}")
        console.print()

    if diff.still_present:
        console.print(f"[bold yellow]⚠️  Remaining Issues ({len(diff.still_present)}):[/]")
        for issue in diff.still_present:
            console.print(f"   [yellow]●[/] {issue.severity.emoji} {issue.vuln_type} at {issue.location}")
        console.print()

    if diff.new_issues:
        console.print(f"[bold red]🆕 New Issues ({len(diff.new_issues)}):[/]")
        for issue in diff.new_issues:
            console.print(f"   [red]●[/] {issue.severity.emoji} {issue.vuln_type} at {issue.location}")
        console.print()


def print_commit_blocked(diff: DiffResult) -> None:
    """Print commit blocked message with issue details."""
    console.print()
    console.print(Panel(
        "[bold red]COMMIT BLOCKED[/]\n\n"
        f"[yellow]{len(diff.still_present)} issue(s) still need to be fixed[/]",
        title="🛡️  PromptSentry",
        border_style="red",
        box=box.DOUBLE,
    ))
    console.print()
    print_diff_result(diff)
    console.print("[dim]💡 Fix the issues above or use: git commit --no-verify[/]")


def print_commit_allowed(diff: Optional[DiffResult] = None) -> None:
    """Print commit allowed message."""
    console.print()
    if diff and diff.fixed:
        console.print(Panel(
            f"[bold green]COMMIT ALLOWED[/]\n\n"
            f"🎉 All {len(diff.fixed)} issue(s) have been resolved!",
            title="🛡️  PromptSentry",
            border_style="green",
            box=box.DOUBLE,
        ))
    else:
        console.print(Panel(
            "[bold green]COMMIT ALLOWED[/]\n\n"
            "✅ All security checks passed!",
            title="🛡️  PromptSentry",
            border_style="green",
            box=box.DOUBLE,
        ))


# ═══════════════════════════════════════════════════════════════════════════════
# ISSUES LIST
# ═══════════════════════════════════════════════════════════════════════════════

def print_issues_list(issues: list[Issue], file_path: Optional[str] = None) -> None:
    """Print a list of tracked issues."""
    if not issues:
        console.print("[dim]No tracked issues[/]")
        return

    title = f"Issues in {file_path}" if file_path else "All Tracked Issues"

    table = Table(
        title=title,
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )

    table.add_column("ID", width=20, style="dim")
    table.add_column("Severity", justify="center", width=10)
    table.add_column("Type", width=20)
    table.add_column("Location", width=25)
    table.add_column("Status", justify="center", width=10)

    for issue in issues:
        status_style = {
            "open": "yellow",
            "fixed": "green",
            "ignored": "dim",
            "false_positive": "cyan",
        }.get(issue.status.value, "white")

        table.add_row(
            issue.issue_id[:16] + "...",
            format_severity(issue.severity),
            issue.vuln_type,
            issue.location,
            f"[{status_style}]{issue.status.value}[/]",
        )

    console.print(table)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def print_config(config: dict) -> None:
    """Print configuration in a nice format."""
    tree = Tree("[bold cyan]🛡️  PromptSentry Configuration[/]")

    def add_items(parent: Tree, data: dict, prefix: str = ""):
        for key, value in data.items():
            if isinstance(value, dict):
                branch = parent.add(f"[bold]{key}[/]")
                add_items(branch, value, prefix + "  ")
            else:
                parent.add(f"[cyan]{key}:[/] {value}")

    add_items(tree, config)
    console.print(tree)


# ═══════════════════════════════════════════════════════════════════════════════
# INITIALIZATION DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def print_init_start() -> None:
    """Print initialization start message."""
    print_banner()
    console.print("[bold]Setting up PromptSentry...[/]")
    console.print()


def print_init_complete() -> None:
    """Print initialization complete message."""
    console.print()
    console.print(Panel(
        "[bold green]Setup Complete![/]\n\n"
        "Next steps:\n"
        "  1. [cyan]cd your-project[/]\n"
        "  2. [cyan]promptsentry install-hook[/]\n"
        "  3. Start committing securely! 🚀",
        title="🛡️  PromptSentry Ready",
        border_style="green",
        box=box.ROUNDED,
    ))
