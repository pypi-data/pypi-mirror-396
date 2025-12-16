"""ASCII mode utilities for mcp-audit TUI.

Provides ASCII alternatives for Unicode characters when running
in environments that don't support Unicode properly.
"""

import os
from typing import Dict

from rich import box


def is_ascii_mode() -> bool:
    """Check if ASCII mode is enabled.

    Returns True if MCP_AUDIT_ASCII environment variable is set to a truthy value.
    """
    ascii_env = os.environ.get("MCP_AUDIT_ASCII", "").lower()
    return ascii_env in ("1", "true", "yes", "on")


def get_box_style() -> box.Box:
    """Get the appropriate box style based on ASCII mode.

    Returns:
        box.ASCII if ASCII mode enabled, otherwise box.ROUNDED
    """
    if is_ascii_mode():
        return box.ASCII
    return box.ROUNDED


# Emoji to ASCII text mapping
EMOJI_TO_ASCII: Dict[str, str] = {
    "📌": "[pin]",
    "💰": "[+$]",
    "💸": "[-$]",
    "🌿": "branch:",
    "📁": "files:",
    "↺": "(sync)",
}


def ascii_emoji(emoji: str) -> str:
    """Convert emoji to ASCII equivalent if in ASCII mode.

    Args:
        emoji: The emoji character to potentially convert

    Returns:
        ASCII equivalent if in ASCII mode, otherwise the original emoji
    """
    if is_ascii_mode():
        return EMOJI_TO_ASCII.get(emoji, emoji)
    return emoji


def format_with_emoji(emoji: str, text: str) -> str:
    """Format text with emoji prefix, respecting ASCII mode.

    Args:
        emoji: The emoji to prepend
        text: The text content

    Returns:
        Formatted string with emoji or ASCII equivalent
    """
    prefix = ascii_emoji(emoji)
    if prefix.startswith("["):
        # ASCII mode - add space after bracket notation
        return f"{prefix} {text}"
    elif prefix.endswith(":"):
        # ASCII mode - colon prefix like "branch:"
        return f"{prefix} {text}"
    else:
        # Unicode mode - emoji with space
        return f"{prefix} {text}"
