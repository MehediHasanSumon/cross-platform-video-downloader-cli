"""Help modal, cookies guide, and exit card."""

import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from core.config import COOKIES_FILE, get_base_download_dir
from ui.theme import Theme

class ModalRenderer:
    """Renders informative popup panels for help, cookies guide, and exit."""

    @staticmethod
    def show_cookies_modal(console: Console):
        has_cookies = os.path.isfile(COOKIES_FILE)

        grid = Table.grid(padding=(0, 1), expand=True)
        grid.add_column()

        status_text = f"[bold {Theme.SUCCESS}]✓ Active & Loaded[/]" if has_cookies else f"[bold {Theme.WARNING}]● Not Found (Public mode active)[/]"

        grid.add_row(Text.from_markup(f"[bold {Theme.PRIMARY}]Current Status:[/] {status_text}"))
        grid.add_row(Text.from_markup(f"[dim]Expected Location: {COOKIES_FILE}[/dim]\n"))

        grid.add_row(Text.from_markup("[bold bright_white]Why do you need cookies.txt?[/bold bright_white]"))
        grid.add_row(Text.from_markup("• Download [bold blue]private Facebook group videos[/bold blue] or friends-only posts."))
        grid.add_row(Text.from_markup("• Download [bold magenta]restricted Instagram reels[/bold magenta] and follower-only media."))
        grid.add_row(Text.from_markup("• Bypass [bold red]YouTube age-restrictions[/bold red] or member-only videos.\n"))

        grid.add_row(Text.from_markup("[bold bright_white]How to set up in 2 minutes:[/bold bright_white]"))
        grid.add_row(Text.from_markup("1. Install a browser extension (e.g. [bold cyan]Get cookies.txt LOCALLY[/bold cyan])."))
        grid.add_row(Text.from_markup("2. Open Facebook / YouTube in your browser while logged in."))
        grid.add_row(Text.from_markup("3. Export cookies and save the file as [bold yellow]cookies.txt[/bold yellow] in this project folder."))
        grid.add_row(Text.from_markup("4. The engine will automatically authenticate all restricted downloads!"))

        panel = Panel(
            grid,
            title=f"[bold {Theme.WARNING}] 🍪 Cookie Authentication Guide [/]",
            border_style=Theme.WARNING,
            box=box.ROUNDED,
            padding=(1, 2),
        )
        console.print()
        console.print(panel)
        console.print()

    @staticmethod
    def show_help_modal(console: Console):
        grid = Table.grid(padding=(0, 1), expand=True)
        grid.add_column()

        grid.add_row(Text.from_markup("[bold bright_white]⚡ Key Commands & Shortcuts:[/bold bright_white]"))
        grid.add_row(Text.from_markup(f"  [bold {Theme.DANGER}]q[/]            : Exit application immediately."))
        grid.add_row(Text.from_markup(f"  [bold {Theme.WARNING}]cookies[/]      : View cookies.txt status & setup instructions."))
        grid.add_row(Text.from_markup(f"  [bold {Theme.PRIMARY}]logs[/]         : Open and inspect download logs in terminal."))
        grid.add_row(Text.from_markup(f"  [bold {Theme.SUCCESS}]clear[/]        : Clear screen and refresh dashboard."))
        grid.add_row(Text.from_markup("  [bold white]Ctrl + C[/bold white]     : Safely cancel current action or download.\n"))

        grid.add_row(Text.from_markup("[bold bright_white]🎯 Navigation & Quality:[/bold bright_white]"))
        grid.add_row(Text.from_markup(f"  • Use [bold {Theme.PRIMARY}]↑ / ↓[/] arrow keys or numbers [bold {Theme.PRIMARY}]1-5[/] to select format quality."))
        grid.add_row(Text.from_markup(f"  • Press [bold {Theme.PRIMARY}]Enter[/] to confirm selection and start lossless merge."))
        grid.add_row(Text.from_markup(f"  • Download folders are auto-sorted into [bold {Theme.PRIMARY}]downloads/<Platform>/[/]."))

        panel = Panel(
            grid,
            title=f"[bold {Theme.PRIMARY}] 💡 Quick Reference & Help [/]",
            border_style=Theme.BORDER,
            box=box.ROUNDED,
            padding=(1, 2),
        )
        console.print()
        console.print(panel)
        console.print()

    @staticmethod
    def render_goodbye_card(console: Console):
        content = Table.grid(expand=True)
        content.add_column(justify="center")
        content.add_row(Text.from_markup(f"[bold {Theme.PRIMARY}]⚡ Thank you for using Video Downloader![/bold {Theme.PRIMARY}]"))
        content.add_row(Text.from_markup("[dim]All downloads are safely stored in your project's downloads/ directory.[/dim]"))
        panel = Panel(
            content,
            border_style=Theme.BORDER,
            box=box.ROUNDED,
            padding=(1, 2),
        )
        console.print()
        console.print(panel)
        console.print()
