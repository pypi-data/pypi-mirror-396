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

# ──────────────────────────────────────────────────────────────────────────────
# RICH-CLICK CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = False
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.SHOW_OPTIONS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.MAX_WIDTH = 100

click.rich_click.STYLE_COMMAND = "bold green"
click.rich_click.STYLE_OPTION = "bold cyan"
click.rich_click.STYLE_ARGUMENT = "bold yellow"
click.rich_click.STYLE_SWITCH = "bold magenta"
click.rich_click.STYLE_METAVAR = "bold blue"
click.rich_click.STYLE_USAGE = "bold yellow"
click.rich_click.STYLE_USAGE_COMMAND = "bold green"

click.rich_click.STYLE_HELPTEXT_FIRST_LINE = "bold"
click.rich_click.STYLE_HELPTEXT = "bold white"
click.rich_click.STYLE_OPTION_HELP = "bold white"
click.rich_click.STYLE_OPTION_DEFAULT = "cyan"

click.rich_click.STYLE_REQUIRED_SHORT = "bold red"
click.rich_click.STYLE_REQUIRED_LONG = "bold red"

click.rich_click.STYLE_ERRORS_SUGGESTION = "bold yellow"
click.rich_click.ERRORS_SUGGESTION = "💡 Try using the --help flag for more information."
click.rich_click.ERRORS_EPILOGUE = ""
click.rich_click.ALIGN_ERRORS_PANEL = "left"

# ──────────────────────────────────────────────────────────────────────────────
# MAIN CLI GROUP
# ──────────────────────────────────────────────────────────────────────────────

@click.group(
    help="""
[bold cyan]🛡️  PromptSentry[/bold cyan] – [bold]AI Prompt Security Scanner[/bold]

Detect and prevent vulnerabilities in AI prompts before they reach production.
Uses [bold]OWASP LLM Top 10 2025[/bold] rules for comprehensive security analysis.

[bold yellow]Quick Start:[/bold yellow]
  [bold white]$[/bold white] [bold green]promptsentry init[/bold green]              # Set up PromptSentry
  [bold white]$[/bold white] [bold green]promptsentry install-hook[/bold green]      # Install git pre-commit hook
  [bold white]$[/bold white] [bold green]promptsentry scan file.py[/bold green]      # Scan a file for vulnerabilities

[bold yellow]Features:[/bold yellow]
  • [bold]3-Stage Analysis[/bold]: Prompt detection → Pattern matching → Optional LLM analysis
  • [bold]Differential Validation[/bold]: Only blocks on unfixed tracked issues
  • [bold]Moving Goalpost Prevention[/bold]: New issues don't block existing work
  • [bold]Git Hook Integration[/bold]: Automatic scanning on commits
  • [bold]SQLite Issue Tracking[/bold]: Persistent vulnerability database

[bold white]Learn more:[/bold white] https://pypi.org/project/promptsentry
""",
)
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-essential output")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def main(ctx: click.Context, quiet: bool, verbose: bool):
    ctx.ensure_object(dict)
    ctx.obj["quiet"] = quiet
    ctx.obj["verbose"] = verbose


# ──────────────────────────────────────────────────────────────────────────────
# INIT COMMAND
# ──────────────────────────────────────────────────────────────────────────────

@main.command()
@click.option("--force", "-f", is_flag=True, help="Force re-initialization")
@click.pass_context
def init(ctx: click.Context, force: bool):
    """
    [bold]Initialize PromptSentry.[/bold]

    Sets up your local environment for scanning:
    • Creates [bold cyan]~/.promptsentry[/bold cyan]
    • Loads [bold]OWASP LLM Top 10 2025[/bold]
    • Starts [bold green]Ollama[/bold green] if needed
    • Downloads [bold yellow]deepseek-r1:1.5b[/bold yellow]

    [bold white]Run once before first use.[/bold white]
    """
    print_init_start()

    config_dir = DEFAULT_CONFIG_DIR

    print_step("Creating configuration directory...", "working")
    config_dir.mkdir(parents=True, exist_ok=True)
    print_step(f"Configuration directory: {config_dir}", "done")

    print_step("Creating default configuration...", "working")
    config = PromptSentryConfig()
    config.save()
    print_step("Configuration saved", "done")

    print_step("Loading OWASP LLM Top 10 2025 rules...", "working")
    try:
        from promptsentry.core.rules_loader import RulesLoader

        loader = RulesLoader()
        loader.initialize()
        print_step(f"OWASP rules loaded ({loader.rule_count} categories)", "done")
    except Exception as e:
        print_step(f"Rules loading failed: {e}", "error")

    print_step("Setting up Ollama...", "working")
    try:
        from promptsentry.llm.ollama_manager import OllamaManager

        success, message = OllamaManager.ensure_ollama_ready(
            model_name=config.llm.model_name or "deepseek-r1:1.5b",
            verbose=ctx.obj.get("verbose", False),
        )

        if success:
            print_step("Ollama ready", "done")
        else:
            print_step(message, "skip")
    except Exception as e:
        print_step("Ollama unavailable (pattern matching only)", "skip")
        if ctx.obj.get("verbose"):
            console.print(f"[dim]{e}[/]")

    print_init_complete()


# ──────────────────────────────────────────────────────────────────────────────
# SCAN COMMAND
# ──────────────────────────────────────────────────────────────────────────────

@main.command()
@click.argument("path", type=click.Path(exists=True), required=False)
@click.option("--staged", is_flag=True, help="Scan staged git files only")
@click.option("--hook", is_flag=True, hidden=True)
@click.option("--no-llm", is_flag=True, help="Disable LLM analysis")
@click.option("--threshold", "-t", type=int, default=50, help="Block threshold (0-100)")
@click.pass_context
def scan(ctx, path, staged, hook, no_llm, threshold):
    """
    [bold]Scan files for AI prompt vulnerabilities.[/bold]

    Detects prompt injection, secret leakage, unsafe execution,
    and OWASP LLM Top 10 violations.
    """
    quiet = ctx.obj.get("quiet", False)
    use_llm = not no_llm

    if staged:
        from promptsentry.git.hook import PreCommitHook

        sys.exit(PreCommitHook(use_llm=use_llm).run())

    if not path:
        print_error("Specify a path or use --staged")
        sys.exit(1)

    path = Path(path)

    if not quiet:
        print_banner(mini=True)
        console.print()

    if path.is_file():
        result = _scan_file(str(path), use_llm)
        if result:
            print_analysis_result(result)
            if result.is_vulnerable:
                sys.exit(1)

    elif path.is_dir():
        results = _scan_directory(path, use_llm, quiet)
        print_scan_summary(results)
        if any(r.is_vulnerable for r in results):
            sys.exit(1)

    sys.exit(0)


def _scan_file(file_path: str, use_llm: bool):
    from promptsentry.core.analyzer import PromptAnalyzer
    from promptsentry.core.detector import PromptDetector
    from promptsentry.core.patterns import PatternMatcher
    from promptsentry.models.vulnerability import AnalysisResult

    detector = PromptDetector()
    prompts = detector.detect_prompts(file_path)

    if not prompts:
        return AnalysisResult(file_path, "", [], 0, False)

    matcher = PatternMatcher()
    matches = []
    for p in prompts:
        matches.extend(matcher.check_patterns(p))

    analyzer = PromptAnalyzer(
        config=PromptSentryConfig.load().llm,
        use_llm=use_llm,
    )
    return analyzer.analyze(prompts[0], matches)


def _scan_directory(directory: Path, use_llm: bool, quiet: bool):
    cfg = PromptSentryConfig.load()
    files = []
    for ext in cfg.scan.file_extensions:
        files.extend(directory.rglob(f"*{ext}"))

    if not files:
        if not quiet:
            print_warning("No scannable files found")
        return []

    results = []
    with create_progress() as progress:
        task = progress.add_task("Scanning...", total=len(files))
        for f in files:
            results.append(_scan_file(str(f), use_llm))
            progress.update(task, advance=1)

    return results


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
