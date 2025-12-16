"""Git integration for PromptSentry."""

from promptsentry.git.hook import PreCommitHook, install_hook, uninstall_hook
from promptsentry.git.staged_files import get_staged_content, get_staged_files

__all__ = [
    "PreCommitHook",
    "install_hook",
    "uninstall_hook",
    "get_staged_files",
    "get_staged_content",
]
