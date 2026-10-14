"""Visual card components for media info, pre-flight summary, and completion."""

import os
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from core.models import MediaInfo, FormatOption, DownloadResult
from core.sanitizer import Sanitizer
from ui.theme import Theme

class CardRenderer:
    """Renders informative metadata cards styled in the pastel dark theme."""

    @staticmethod
    def render_media_card(console: Console, media: MediaInfo):
        """Displays detected media information before quality selection."""
        table = Table.grid(padding=(0, 2))
        table.add_column("Key", style=f"bold {Theme.PRIMARY}", justify="right", width=14)
        table.add_column("Value", style="white")

        table.add_row("Platform:", media.platform.badge)
        table.add_row("Title:", f"[bold {Theme.TEXT_LIGHT}]{media.title}[/]")
        table.add_row("Author / Page:", f"[{Theme.WARNING}]{media.uploader}[/]")

        if media.is_playlist:
            count = media.playlist_count or "Multiple"
            table.add_row("Content:", f"[bold {Theme.ACCENT}]Playlist / Collection ({count} items)[/]")
        else:
            duration_str = Sanitizer.format_duration(media.duration)
            views_str = Sanitizer.format_views(media.views)
            table.add_row("Duration:", f"[{Theme.SUCCESS}]{duration_str}[/]")
            if views_str != "N/A":
                table.add_row("Views:", f"[{Theme.TEXT_LIGHT}]{views_str}[/]")
            table.add_row("Content:", f"[bold {Theme.PRIMARY}]{media.platform.name} Media[/]")

        source_display = media.url if len(media.url) <= 65 else media.url[:62] + "..."
        table.add_row("Source URL:", f"[dim]{source_display}[/dim]")

        panel = Panel(
            table,
            title=f"[bold {Theme.TEXT_LIGHT}] {media.platform.icon} Media Information [/]",
            border_style=Theme.BORDER,
            box=box.ROUNDED,
            padding=(1, 2),
        )
        console.print()
        console.print(panel)
        console.print()

    @staticmethod
    def render_preflight_card(console: Console, media: MediaInfo, format_option: FormatOption, dest_path: str):
        """Renders summary before starting download execution."""
        table = Table.grid(padding=(0, 2))
        table.add_column("Key", style=f"bold {Theme.PRIMARY}", justify="right", width=14)
        table.add_column("Value", style="white")

        table.add_row("Platform:", media.platform.badge)
        table.add_row("Target:", f"[bold {Theme.TEXT_LIGHT}]{media.title}[/]")
        table.add_row("Quality:", f"[{Theme.WARNING}]{format_option.name}[/] [{Theme.PRIMARY}]({format_option.badge})[/]")
        table.add_row("Codec:", f"[dim]{format_option.codec}[/dim]")
        est_size = format_option.estimated_size_str(media.duration)
        table.add_row("Est. Size:", f"[{Theme.SUCCESS}]{est_size}[/]")

        if media.is_playlist:
            clean_folder = Sanitizer.clean_media_title({"title": media.title}, "generic")
            playlist_dest = os.path.join(dest_path, clean_folder)
            table.add_row("Destination:", f"[{Theme.PRIMARY}]{playlist_dest}[/]")
            count_info = f"{media.playlist_count} items" if media.playlist_count else "Multiple items"
            if media.playlist_items_range:
                count_info += f" [bold {Theme.WARNING}](Range: {media.playlist_items_range})[/]"
            table.add_row("Playlist Items:", f"[{Theme.ACCENT}]{count_info}[/]")
            table.add_row("Serial Format:", f"[{Theme.SUCCESS}]01. Title.ext, 02. Title.ext ...[/]")
        else:
            table.add_row("Destination:", f"[{Theme.PRIMARY}]{dest_path}[/]")

        table.add_row("Smart Resume:", f"[{Theme.SUCCESS}]Active (.part files auto-resume)[/]")
        table.add_row("Disk Check:", f"[{Theme.SUCCESS}]Active (Existing files > 1KB skipped)[/]")

        panel = Panel(
            table,
            title=f"[bold {Theme.PRIMARY}] Pre-Download Summary [/]",
            border_style=Theme.BORDER,
            box=box.ROUNDED,
            padding=(1, 2),
        )
        console.print(panel)
        console.print()

    @staticmethod
    def render_success_card(console: Console, result: DownloadResult):
        """Renders download summary upon completion."""
        num_completed = len(result.completed_files)
        num_skipped = len(result.skipped_files)
        num_failed = len(result.failed_files)
        elapsed_str = Sanitizer.format_duration(result.elapsed_seconds)

        table = Table.grid(padding=(0, 2))
        table.add_column("Key", style=f"bold {Theme.PRIMARY}", justify="right", width=14)
        table.add_column("Value", style="white")

        table.add_row("Status:", f"[bold {Theme.SUCCESS}]✓ Download Complete[/]")
        table.add_row("Media Title:", f"[bold {Theme.TEXT_LIGHT}]{result.title}[/]")
        table.add_row("Saved In:", f"[{Theme.PRIMARY}]{result.destination_path}[/]")
        table.add_row("Elapsed Time:", f"[{Theme.MUTED}]{elapsed_str}[/]")

        if result.is_playlist or (num_completed + num_skipped + num_failed > 1):
            table.add_row("New Downloads:", f"[bold {Theme.SUCCESS}]{num_completed}[/] files")
            table.add_row("Skipped Existing:", f"[bold {Theme.WARNING}]{num_skipped}[/] files")
            if num_failed > 0:
                table.add_row("Failed/Unavailable:", f"[bold {Theme.DANGER}]{num_failed}[/] files")
            table.add_row("Total Processed:", f"[bold {Theme.PRIMARY}]{num_completed + num_skipped + num_failed}[/] items")

        panel = Panel(
            table,
            title=f"[bold {Theme.SUCCESS}] ✨ Download Completed Successfully [/]",
            border_style=Theme.SUCCESS,
            box=box.ROUNDED,
            padding=(1, 2),
        )
        console.print()
        console.print(panel)
        console.print()
