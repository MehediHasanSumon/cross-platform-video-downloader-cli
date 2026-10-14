"""Interactive terminal menus with arrow key, numeric, and hotkey navigation."""

import sys
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.prompt import Prompt
from rich import box
from core.models import FormatOption, MediaInfo
from core.config import POST_DOWNLOAD_ACTIONS
from ui.theme import Theme
from utils.terminal import read_key

class MenuRenderer:
    """Manages interactive selection menus."""

    @staticmethod
    def render_format_table(
        selected_index: int,
        profiles: List[FormatOption],
        platform_name: str,
        duration: Optional[int] = None,
    ) -> Panel:
        table = Table(show_header=True, header_style="bold bright_white", box=None, padding=(0, 1), expand=True)
        table.add_column("Key", width=6, justify="center")
        table.add_column("Quality & Format", width=28)
        table.add_column("Est. Size", width=12, justify="center")
        table.add_column("Tag", width=14, justify="center")
        table.add_column("Description", style="dim")

        for idx, prof in enumerate(profiles):
            num = idx + 1
            tag = f"[{prof.tag_color}][{prof.tag}][/{prof.tag_color}]"
            est_size = prof.estimated_size_str(duration)

            if idx == selected_index:
                table.add_row(
                    f"[bold {Theme.PRIMARY}]> [{num}][/]",
                    f"[bold {Theme.TEXT_LIGHT}]{prof.name}[/]",
                    f"[bold {Theme.SUCCESS}]{est_size}[/]",
                    tag,
                    f"[{Theme.TEXT_LIGHT}]{prof.desc}[/]",
                )
            else:
                table.add_row(
                    f"  [dim][{num}][/dim]",
                    f"[dim]{prof.name}[/dim]",
                    f"[dim]{est_size}[/dim]",
                    f"[dim]{prof.tag}[/dim]",
                    f"[dim]{prof.desc}[/dim]",
                )

        return Panel(
            table,
            title=f"[bold {Theme.PRIMARY}] Select Quality & Format ({platform_name}) [/]",
            subtitle="[dim]Use Up/Down arrows or keys 1-5, Enter to confirm[/dim]",
            border_style=Theme.BORDER,
            box=box.ROUNDED,
            padding=(1, 1),
        )

    @classmethod
    def interactive_format_menu(
        cls,
        console: Console,
        profiles: List[FormatOption],
        platform_name: str,
        duration: Optional[int] = None,
        default_index: int = 0,
    ) -> int:
        num_options = len(profiles)
        selected = min(default_index, num_options - 1)

        if not sys.stdin.isatty():
            console.print(cls.render_format_table(selected, profiles, platform_name, duration))
            choice = Prompt.ask("  Select format", choices=[str(i + 1) for i in range(num_options)], default="1")
            return int(choice) - 1

        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        try:
            with Live(cls.render_format_table(selected, profiles, platform_name, duration), console=console, auto_refresh=False) as live:
                while True:
                    key = read_key()
                    if key in ("UP", "k", "K", "w", "W"):
                        selected = (selected - 1) % num_options
                        live.update(cls.render_format_table(selected, profiles, platform_name, duration), refresh=True)
                    elif key in ("DOWN", "j", "J", "s", "S"):
                        selected = (selected + 1) % num_options
                        live.update(cls.render_format_table(selected, profiles, platform_name, duration), refresh=True)
                    elif key.isdigit() and 1 <= int(key) <= num_options:
                        selected = int(key) - 1
                        live.update(cls.render_format_table(selected, profiles, platform_name, duration), refresh=True)
                        break
                    elif key in ("ENTER", "SPACE"):
                        break
                    elif key in ("ESC", "q", "Q"):
                        selected = 0
                        break
                    elif key == "CTRL_C":
                        raise KeyboardInterrupt
        finally:
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()

        chosen = profiles[selected]
        console.print(f"  [bold {Theme.SUCCESS}]✓ Selected Format:[/] [bold {Theme.TEXT_LIGHT}]{chosen.name}[/] [dim]({chosen.badge})[/dim]\n")
        return selected

    @staticmethod
    def select_playlist_mode(console: Console, media: MediaInfo) -> bool:
        """Prompts user whether to download the entire playlist or only the single targeted video."""
        options = [
            f"Download Entire Playlist ({media.playlist_count or 'All'} videos)",
            "Download Only This Single Video",
        ]

        def get_panel(sel: int):
            table = Table.grid(padding=(0, 1), expand=True)
            table.add_column()
            table.add_row(f"[{Theme.WARNING}]Notice: Video in Playlist Detected[/]")
            table.add_row("[dim]This link points to a single video that also belongs to a playlist.[/dim]\n")

            for idx, opt in enumerate(options):
                num = idx + 1
                if idx == sel:
                    table.add_row(f"[bold {Theme.PRIMARY}]> [{num}] {opt}[/]")
                else:
                    table.add_row(f"  [dim][{num}] {opt}[/dim]")

            return Panel(
                table,
                title=f"[bold {Theme.PRIMARY}] Playlist Selection [/]",
                subtitle="[dim]Use Up/Down arrows or 1/2, Enter to confirm[/dim]",
                border_style=Theme.BORDER,
                box=box.ROUNDED,
                padding=(1, 2),
            )

        if not sys.stdin.isatty():
            console.print(get_panel(0))
            choice = Prompt.ask("  Choose mode", choices=["1", "2"], default="1")
            return choice == "1"

        selected = 0
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        try:
            with Live(get_panel(selected), console=console, auto_refresh=False) as live:
                while True:
                    key = read_key()
                    if key in ("UP", "DOWN", "k", "j", "w", "s"):
                        selected = 1 - selected
                        live.update(get_panel(selected), refresh=True)
                    elif key in ("1", "2"):
                        selected = int(key) - 1
                        live.update(get_panel(selected), refresh=True)
                        break
                    elif key in ("ENTER", "SPACE"):
                        break
                    elif key in ("ESC", "q", "Q"):
                        selected = 0
                        break
                    elif key == "CTRL_C":
                        raise KeyboardInterrupt
        finally:
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()

        console.print(f"  [bold {Theme.SUCCESS}]✓ Mode:[/] [bold {Theme.TEXT_LIGHT}]{options[selected]}[/]\n")
        return selected == 0

    @staticmethod
    def render_post_download_table(selected_index: int) -> Panel:
        table = Table.grid(padding=(0, 2), expand=True)
        table.add_column("Key", width=6, justify="center")
        table.add_column("Option", style="white")

        hotkeys = ["[1/n]", "[2/o]", "[3/p]", "[4/l]", "[5/q]"]
        for idx, opt in enumerate(POST_DOWNLOAD_ACTIONS):
            num = idx + 1
            hk = hotkeys[idx] if idx < len(hotkeys) else f"[{num}]"
            if idx == selected_index:
                table.add_row(
                    f"[bold {Theme.PRIMARY}]> {hk}[/]",
                    f"[bold {Theme.TEXT_LIGHT}]{opt}[/]",
                )
            else:
                table.add_row(f"  [dim]{hk}[/dim]", f"[dim]{opt}[/dim]")

        return Panel(
            table,
            title=f"[bold {Theme.PRIMARY}] What would you like to do next? [/]",
            subtitle="[dim]Hotkeys: (o)=Open Folder • (p)=Play • (n)=Next • (q)=Quit • (↑/↓)[/dim]",
            border_style=Theme.BORDER,
            box=box.ROUNDED,
            padding=(1, 2),
        )

    @classmethod
    def interactive_post_download_menu(cls, console: Console, default_index: int = 0) -> int:
        num_options = len(POST_DOWNLOAD_ACTIONS)
        selected = default_index

        if not sys.stdin.isatty():
            console.print(cls.render_post_download_table(selected))
            choice = Prompt.ask("  Choose action", choices=[str(i + 1) for i in range(num_options)], default=str(default_index + 1))
            return int(choice) - 1

        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        try:
            with Live(cls.render_post_download_table(selected), console=console, auto_refresh=False) as live:
                while True:
                    key = read_key()
                    if key in ("UP", "k", "K", "w", "W"):
                        selected = (selected - 1) % num_options
                        live.update(cls.render_post_download_table(selected), refresh=True)
                    elif key in ("DOWN", "j", "J", "s", "S"):
                        selected = (selected + 1) % num_options
                        live.update(cls.render_post_download_table(selected), refresh=True)
                    elif key.isdigit() and 1 <= int(key) <= num_options:
                        selected = int(key) - 1
                        break
                    elif key.lower() == "n":
                        selected = 0
                        break
                    elif key.lower() == "o":
                        selected = 1
                        break
                    elif key.lower() == "p":
                        selected = 2
                        break
                    elif key.lower() == "l":
                        selected = 3
                        break
                    elif key.lower() == "q" or key == "ESC":
                        selected = 4
                        break
                    elif key in ("ENTER", "SPACE"):
                        break
                    elif key == "CTRL_C":
                        raise KeyboardInterrupt
        finally:
            sys.stdout.write("\033[?25h")
            sys.stdout.flush()

        chosen = POST_DOWNLOAD_ACTIONS[selected]
        console.print(f"  [bold {Theme.SUCCESS}]✓ Action:[/] [bold {Theme.TEXT_LIGHT}]{chosen}[/]\n")
        return selected
