"""Header, banner, and input prompt rendering."""

import sys
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from core.config import VERSION, AUTHOR
from ui.theme import Theme
from utils.system import SystemUtils

class BannerRenderer:
    """Renders the top hero banner and interactive input prompts."""

    @staticmethod
    def render_header(console: Console):
        os_name = "Windows" if sys.platform == "win32" else ("macOS" if sys.platform == "darwin" else "Linux")

        content = Table.grid(expand=True)
        content.add_column(justify="center")

        # 1. Hero Brand Title in bold, prominent normal font with TrueColor gradient (no letter spaces)
        title = Theme.apply_title_gradient("VIDEO DOWNLOADER")
        sub = Text.from_markup(f"[{Theme.MUTED}]Developed by[/] [bold white]{AUTHOR}[/]")

        # 2. Supported Platforms Ribbon with compact sleek badges
        platforms = Text.from_markup(
            f"[bold {Theme.TEXT_DARK} on #f87070] YouTube [/]  "
            f"[bold {Theme.TEXT_DARK} on #60a4fa] Facebook [/]  "
            f"[bold {Theme.TEXT_DARK} on #e778f9] Instagram [/]  "
            f"[bold {Theme.TEXT_DARK} on #27d2ed] TikTok [/]  "
            f"[bold {Theme.TEXT_DARK} on #f3f4f6] Twitter [/]  "
        )

        # 3. System Specs Line with colored indicator dots
        status_line = Text.from_markup(
            f"[{Theme.PRIMARY}]●[/] [bold {Theme.TEXT_LIGHT}]Engine: YT-DLP[/]   "
            f"[{Theme.SUCCESS}]●[/] [bold {Theme.TEXT_LIGHT}]OS: {os_name}[/]   "
            f"[{Theme.ACCENT}]●[/] [bold {Theme.TEXT_LIGHT}]Version {VERSION}[/]"
        )

        content.add_row(title)
        content.add_row(sub)
        content.add_row(Text(""))
        content.add_row(platforms)
        content.add_row(Text(""))
        content.add_row(status_line)

        banner = Panel(
            content,
            border_style=Theme.BORDER,
            box=box.ROUNDED,
            padding=(1, 2),
        )
        console.print(banner)
        console.print()

    @staticmethod
    def render_input_prompt(console: Console, clipboard_candidate: Optional[str] = None):
        """Displays the URL entry prompt with optional clipboard link suggestion."""
        if clipboard_candidate:
            short_url = clipboard_candidate if len(clipboard_candidate) <= 65 else clipboard_candidate[:62] + "..."
            console.print(f"  [{Theme.SUCCESS}]📋 Found link in clipboard:[/] [bold {Theme.TEXT_LIGHT}]{short_url}[/]")
            console.print(f"  [dim](Press Enter directly to use this link, or paste a new URL)[/dim]")

        console.print(f"[bold {Theme.PRIMARY}]Enter Media URL (YouTube, Facebook, Reels, Shorts, etc.):[/bold {Theme.PRIMARY}]")
        console.print(f"[{Theme.MUTED}](Type 'q' to quit)[/{Theme.MUTED}]")
