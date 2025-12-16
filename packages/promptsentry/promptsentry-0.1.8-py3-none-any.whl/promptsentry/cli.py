"""
PromptSentry CLI

Beautiful command-line interface using Rich for terminal output.
Provides commands for scanning, hook management, and configuration.
"""

import sys
from pathlib import Path
from typing import Optional

import rich_click as click

from promptsentry import __version__
from promptsentry.models.config import DEFAULT_CONFIG_DIR, PromptSentryConfig
from promptsentry.utils.formatting import (
    console,
    create_progress,
    print_analysis_result,
    print_banner,
    print_config,
    print_error,
    print_init_complete,
    print_init_start,
    print_issues_list,
    print_scan_summary,
    print_step,
    print_success,
    print_warning,
)

# Configure rich-click for beautiful help formatting
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = False
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_ERRORS_SUGGESTION = "bold yellow"
click.rich_click.ERRORS_SUGGESTION = "💡 Try using the --help flag for more information."
click.rich_click.ERRORS_EPILOGUE = ""
click.rich_click.MAX_WIDTH = 100
click.rich_click.STYLE_OPTION = "bold cyan"
click.rich_click.STYLE_ARGUMENT = "bold yellow"
click.rich_click.STYLE_COMMAND = "bold green"
click.rich_click.STYLE_SWITCH = "bold magenta"
click.rich_click.STYLE_METAVAR = "bold blue"
click.rich_click.STYLE_USAGE = "bold yellow"
click.rich_click.STYLE_USAGE_COMMAND = "bold green"
click.rich_click.STYLE_HELPTEXT_FIRST_LINE = "bold"
click.rich_click.STYLE_HELPTEXT = "dim"
click.rich_click.STYLE_OPTION_HELP = ""
click.rich_click.STYLE_OPTION_DEFAULT = "dim"
click.rich_click.STYLE_REQUIRED_SHORT = "red"
click.rich_click.STYLE_REQUIRED_LONG = "dim red"
click.rich_click.ALIGN_ERRORS_PANEL = "left"

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CLI GROUP
# ═══════════════════════════════════════════════════════════════════════════════

@click.group()
@click.version_option(version=__version__, prog_name="promptsentry")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def main(ctx: click.Context, quiet: bool, verbose: bool):
    """
    [bold cyan]🛡️  PromptSentry[/bold cyan] - AI Prompt Security Scanner

    Detect and prevent vulnerabilities in AI prompts before they reach production.
    Uses [bold]OWASP LLM Top 10 2025[/bold] rules for comprehensive security analysis.

    [bold yellow]Quick Start:[/bold yellow]
      [dim]$[/dim] [bold green]promptsentry init[/bold green]              # Set up PromptSentry
      [dim]$[/dim] [bold green]promptsentry install-hook[/bold green]      # Install git pre-commit hook
      [dim]$[/dim] [bold green]promptsentry scan file.py[/bold green]      # Scan a file for vulnerabilities

    [bold yellow]Features:[/bold yellow]
      • [bold]3-Stage Analysis[/bold]: Prompt detection → Pattern matching → Optional LLM analysis
      • [bold]Differential Validation[/bold]: Only blocks on unfixed tracked issues
      • [bold]Moving Goalpost Prevention[/bold]: New issues don't block existing work
      • [bold]Git Hook Integration[/bold]: Automatic scanning on commits
      • [bold]SQLite Issue Tracking[/bold]: Persistent vulnerability database

    [dim]Learn more at: https://github.com.promptsentry.promptsentry[/dim]
    """
    ctx.ensure_object(dict)
    ctx.obj["quiet"] = quiet
    ctx.obj["verbose"] = verbose


# ═══════════════════════════════════════════════════════════════════════════════
# INIT COMMAND
# ═══════════════════════════════════════════════════════════════════════════════

@main.command()
@click.option("--force", "-f", is_flag=True, help="Force re-initialization")
@click.pass_context
def init(ctx: click.Context, force: bool):
    """
    [bold]Initialize PromptSentry.[/bold]

    Sets up your local environment for scanning. This command:
    • Creates [cyan]~/.promptsentry[/cyan] configuration directory
    • Loads [bold]OWASP LLM Top 10 2025[/bold] rules
    • Auto-starts [green]Ollama[/green] if not running
    • Downloads [yellow]qwen2.5-coder:0.5b[/yellow] model if needed

    [dim]Run this once before using PromptSentry for the first time.[/dim]
    """
    print_init_start()

    config_dir = DEFAULT_CONFIG_DIR

    # Step 1: Create config directory
    print_step("Creating configuration directory...", "working")
    config_dir.mkdir(parents=True, exist_ok=True)
    print_step(f"Configuration directory: {config_dir}", "done")

    # Step 2: Create default config
    print_step("Creating default configuration...", "working")
    config = PromptSentryConfig()
    config.save()
    print_step("Configuration saved", "done")

    # Step 3: Load OWASP rules
    print_step("Loading OWASP LLM Top 10 2025 rules...", "working")
    try:
        from promptsentry.core.rules_loader import RulesLoader

        rules_loader = RulesLoader()
        rules_loader.initialize()
        print_step(f"OWASP rules loaded ({rules_loader.rule_count} categories)", "done")
    except Exception as e:
        print_step(f"Rules loading failed: {e}", "error")

    # Step 4: Ensure Ollama is running and model is available
    print_step("Setting up Ollama...", "working")
    try:
        from promptsentry.llm.ollama_manager import OllamaManager

        # This will automatically:
        # 1. Start Ollama if not running
        # 2. Download model if not available
        success, message = OllamaManager.ensure_ollama_ready(
            model_name=config.llm.model_name or "qwen2.5-coder:0.5b",
            verbose=ctx.obj.get("verbose", False)
        )

        if success:
            print_step(f"Ollama ready: {config.llm.model_name or 'qwen2.5-coder:0.5b'}", "done")
        else:
            print_step(message, "skip")
            if ctx.obj.get("verbose"):
                console.print("   [dim]PromptSentry will work without LLM analysis[/]")
    except Exception as e:
        print_step("Ollama setup failed (will use pattern matching only)", "skip")
        if ctx.obj.get("verbose"):
            console.print(f"   [dim]Error: {e}[/]")

    print_init_complete()


# ═══════════════════════════════════════════════════════════════════════════════
# SCAN COMMAND
# ═══════════════════════════════════════════════════════════════════════════════

@main.command()
@click.argument("path", type=click.Path(exists=True), required=False)
@click.option("--staged", is_flag=True, help="Scan staged git files only")
@click.option("--hook", is_flag=True, hidden=True, help="Called from git hook")
@click.option("--no-llm", is_flag=True, help="Disable LLM analysis (faster but less thorough)")
@click.option("--threshold", "-t", type=int, default=50, help="Block threshold (0-100)")
@click.pass_context
def scan(
    ctx: click.Context,
    path: Optional[str],
    staged: bool,
    hook: bool,
    no_llm: bool,
    threshold: int,
):
    """
    [bold]Scan files for AI prompt vulnerabilities.[/bold]

    Analyzes Python files for security issues in AI prompts using OWASP LLM Top 10 rules.
    Detects issues like prompt injection, API key exposure, and unsafe code execution.

    [bold yellow]Examples:[/bold yellow]
      [dim]$[/dim] [bold green]promptsentry scan chatbot.py[/bold green]          # Scan single file
      [dim]$[/dim] [bold green]promptsentry scan .[/bold green]                   # Scan current directory
      [dim]$[/dim] [bold green]promptsentry scan --staged[/bold green]            # Scan staged files (git)
      [dim]$[/dim] [bold green]promptsentry scan --no-llm file.py[/bold green]    # Fast scan without LLM
    """
    quiet = ctx.obj.get("quiet", False)
    use_llm = not no_llm  # LLM enabled by default

    if staged:
        # Scan staged files using git hook
        exit_code = _run_staged_scan(use_llm=use_llm, quiet=quiet or hook)
        sys.exit(exit_code)

    if not path:
        print_error("Please specify a path to scan or use --staged")
        sys.exit(1)

    path = Path(path)

    if not quiet:
        print_banner(mini=True)
        console.print()

    if path.is_file():
        # Scan single file
        results = _scan_file(str(path), use_llm=use_llm)
        if results:
            print_analysis_result(results)
            if results.is_vulnerable:
                sys.exit(1)
    elif path.is_dir():
        # Scan directory
        results = _scan_directory(path, use_llm=use_llm, quiet=quiet)
        print_scan_summary(results)

        vulnerable_count = sum(1 for r in results if r.is_vulnerable)
        if vulnerable_count > 0:
            sys.exit(1)

    sys.exit(0)


def _run_staged_scan(use_llm: bool, quiet: bool) -> int:
    """Run scan on staged files via git hook."""
    from promptsentry.git.hook import PreCommitHook

    hook = PreCommitHook(use_llm=use_llm)
    return hook.run()


def _scan_file(file_path: str, use_llm: bool = False):
    """Scan a single file."""
    from promptsentry.core.analyzer import PromptAnalyzer
    from promptsentry.core.detector import PromptDetector
    from promptsentry.core.patterns import PatternMatcher
    from promptsentry.models.config import PromptSentryConfig
    from promptsentry.models.vulnerability import AnalysisResult

    config = PromptSentryConfig.load()

    # Stage 1: Detect
    detector = PromptDetector()
    prompts = detector.detect_prompts(file_path)

    if not prompts:
        return AnalysisResult(
            file_path=file_path,
            prompt_location="",
            vulnerabilities=[],
            overall_score=0,
            is_vulnerable=False,
        )

    # Stage 2: Pattern Matching
    pattern_matcher = PatternMatcher()
    all_pattern_matches = []

    for prompt in prompts:
        matches = pattern_matcher.check_patterns(prompt)
        all_pattern_matches.extend(matches)

    # Stage 3: SLM Analyzer (with OWASP rules as context)
    analyzer = PromptAnalyzer(config=config.llm, use_llm=use_llm)

    # Analyze first prompt (simplification)
    # The analyzer will use Ollama with comprehensive OWASP LLM Top 10 2025 rules
    result = analyzer.analyze(prompts[0], all_pattern_matches)

    return result


def _scan_directory(
    directory: Path,
    use_llm: bool = False,
    quiet: bool = False,
) -> list:
    """Scan all files in a directory."""
    from promptsentry.models.config import PromptSentryConfig

    config = PromptSentryConfig.load()
    results = []

    # Find all scannable files
    files = []
    for ext in config.scan.file_extensions:
        files.extend(directory.rglob(f"*{ext}"))

    # Filter excluded patterns
    def is_excluded(file_path: Path) -> bool:
        path_str = str(file_path)
        for pattern in config.scan.exclude_patterns:
            if pattern.replace("**", "").replace("*", "") in path_str:
                return True
        return False

    files = [f for f in files if not is_excluded(f)]

    if not files:
        if not quiet:
            print_warning("No scannable files found")
        return results

    if not quiet:
        console.print(f"Scanning {len(files)} file(s)...")
        console.print()

    with create_progress() as progress:
        task = progress.add_task("Scanning...", total=len(files))

        for file_path in files:
            result = _scan_file(str(file_path), use_llm=use_llm)
            if result:
                results.append(result)
            progress.update(task, advance=1)

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# HOOK COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@main.command("install-hook")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing hook")
@click.pass_context
def install_hook_cmd(ctx: click.Context, force: bool):
    """
    Install the git pre-commit hook.

    The hook will automatically scan staged files for vulnerabilities
    and block commits that contain unfixed security issues.
    """
    from promptsentry.git.hook import install_hook
    from promptsentry.git.staged_files import is_git_repository

    if not is_git_repository():
        print_error("Not in a git repository")
        sys.exit(1)

    print_banner(mini=True)
    console.print()

    if install_hook(force=force):
        console.print()
        console.print("[dim]The hook will now scan staged files before each commit.[/]")
        console.print("[dim]Use 'git commit --no-verify' to bypass if needed.[/]")
    else:
        sys.exit(1)


@main.command("uninstall-hook")
@click.pass_context
def uninstall_hook_cmd(ctx: click.Context):
    """Uninstall the git pre-commit hook."""
    from promptsentry.git.hook import uninstall_hook

    if not uninstall_hook():
        sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# ISSUES COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@main.group()
def issues():
    """Manage tracked security issues."""
    pass


@issues.command("list")
@click.option("--file", "-f", "file_path", help="Show issues for specific file")
@click.option("--all", "-a", "show_all", is_flag=True, help="Show all issues including fixed")
@click.pass_context
def issues_list(ctx: click.Context, file_path: Optional[str], show_all: bool):
    """List tracked security issues."""
    from promptsentry.models.issue import IssueStatus
    from promptsentry.tracker.database import IssueDatabase

    print_banner(mini=True)
    console.print()

    db = IssueDatabase()
    db.initialize()

    if file_path:
        issues = db.get_issues_for_file(file_path)
    else:
        if show_all:
            issues = db.get_all_issues()
        else:
            issues = db.get_all_issues(status=IssueStatus.OPEN)

    print_issues_list(issues, file_path)


@issues.command("clear")
@click.argument("file_path", type=click.Path(exists=True))
@click.confirmation_option(prompt="Are you sure you want to clear issues for this file?")
@click.pass_context
def issues_clear(ctx: click.Context, file_path: str):
    """Clear tracked issues for a file."""
    from promptsentry.tracker.differential import DifferentialValidator

    validator = DifferentialValidator()
    validator.clear_file(file_path)
    print_success(f"Cleared issues for {file_path}")


@issues.command("ignore")
@click.argument("issue_id")
@click.pass_context
def issues_ignore(ctx: click.Context, issue_id: str):
    """Mark an issue as ignored (won't block commits)."""
    from promptsentry.tracker.differential import DifferentialValidator

    validator = DifferentialValidator()
    validator.ignore_issue(issue_id)
    print_success(f"Issue {issue_id} marked as ignored")


@issues.command("stats")
@click.pass_context
def issues_stats(ctx: click.Context):
    """Show issue statistics."""
    from rich import box
    from rich.table import Table

    from promptsentry.tracker.database import IssueDatabase

    print_banner(mini=True)
    console.print()

    db = IssueDatabase()
    db.initialize()
    stats = db.get_stats()

    table = Table(title="Issue Statistics", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    table.add_row("Tracked Files", str(stats["tracked_files"]))
    table.add_row("Open Issues", f"[yellow]{stats['issues']['open']}[/]")
    table.add_row("Fixed Issues", f"[green]{stats['issues']['fixed']}[/]")
    table.add_row("Ignored Issues", f"[dim]{stats['issues']['ignored']}[/]")
    table.add_row("Total Issues", str(stats["issues"]["total"]))

    console.print(table)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@main.group()
def config():
    """Manage PromptSentry configuration."""
    pass


@config.command("show")
@click.pass_context
def config_show(ctx: click.Context):
    """Show current configuration."""
    print_banner(mini=True)
    console.print()

    cfg = PromptSentryConfig.load()
    print_config(cfg.model_dump())


@config.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def config_set(ctx: click.Context, key: str, value: str):
    """
    Set a configuration value.

    \b
    Examples:
      $ promptsentry config set scan.threshold 80
      $ promptsentry config set hook.block_on_issues true
    """
    cfg = PromptSentryConfig.load()

    # Parse key path
    parts = key.split(".")

    try:
        # Navigate to parent
        obj = cfg
        for part in parts[:-1]:
            obj = getattr(obj, part)

        # Get current type and convert value
        current = getattr(obj, parts[-1])
        if isinstance(current, bool):
            value = value.lower() in ("true", "1", "yes")
        elif isinstance(current, int):
            value = int(value)
        elif isinstance(current, float):
            value = float(value)

        # Set value
        setattr(obj, parts[-1], value)
        cfg.save()

        print_success(f"Set {key} = {value}")

    except (AttributeError, ValueError) as e:
        print_error(f"Invalid configuration key or value: {e}")
        sys.exit(1)


@config.command("reset")
@click.confirmation_option(prompt="Reset configuration to defaults?")
@click.pass_context
def config_reset(ctx: click.Context):
    """Reset configuration to defaults."""
    cfg = PromptSentryConfig()
    cfg.save()
    print_success("Configuration reset to defaults")


# ═══════════════════════════════════════════════════════════════════════════════
# RULES COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@main.command("rules")
@click.pass_context
def rules_list(ctx: click.Context):
    """List all vulnerability detection rules."""
    from rich import box
    from rich.table import Table

    from promptsentry.core.patterns import PatternMatcher

    print_banner(mini=True)
    console.print()

    matcher = PatternMatcher()
    rules = matcher.get_applicable_rules()

    table = Table(title="Vulnerability Detection Rules", box=box.ROUNDED)
    table.add_column("ID", style="cyan", width=25)
    table.add_column("Severity", justify="center", width=10)
    table.add_column("OWASP", width=8)
    table.add_column("Description", width=45)

    for rule in sorted(rules, key=lambda r: r["severity"] or "MEDIUM"):
        severity = rule["severity"] or "MEDIUM"
        severity_color = {
            "CRITICAL": "red bold",
            "HIGH": "red",
            "MEDIUM": "yellow",
            "LOW": "blue",
        }.get(severity, "white")

        table.add_row(
            rule["id"],
            f"[{severity_color}]{severity}[/]",
            rule["owasp"] or "-",
            (rule["description"] or "")[:45],
        )

    console.print(table)
    console.print()
    console.print(f"[dim]Total: {len(rules)} rules based on OWASP LLM Top 10[/]")


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
