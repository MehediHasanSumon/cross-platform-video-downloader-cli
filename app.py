"""Application orchestrator and controller for Video Downloader."""

import os
import sys
from typing import Optional, List
from rich.console import Console
from rich.prompt import Prompt

from core.config import (
    ROOT_DIR,
    DEFAULT_DOWNLOAD_DIR,
    YOUTUBE_FORMAT_PROFILES,
    SOCIAL_FORMAT_PROFILES,
    COOKIES_FILE,
)
from core.models import MediaInfo, FormatOption, DownloadResult
from core.logger import AppLogger, view_recent_logs
from core.detector import PlatformDetector
from core.sanitizer import Sanitizer
from downloader.engine import MediaDownloader
from ui.theme import Theme
from ui.banner import BannerRenderer
from ui.cards import CardRenderer
from ui.menus import MenuRenderer
from ui.modals import ModalRenderer
from utils.terminal import clear_terminal, cleanup_terminal
from utils.clipboard import ClipboardHelper
from utils.system import SystemUtils

class MediaDownloaderApp:
    """Main application controller orchestrating user interaction and download workflows."""

    def __init__(self):
        self._ensure_ffmpeg_path()
        self.console = Console(highlight=False)
        self.logger = AppLogger.get_logger()
        self.downloader = MediaDownloader(self.console)
        self.cookies_browser: Optional[str] = None

    def _ensure_ffmpeg_path(self):
        """Adds bundled ffmpeg/bin to PATH if present locally."""
        local_ffmpeg = os.path.join(ROOT_DIR, "ffmpeg", "bin")
        if os.path.isdir(local_ffmpeg) and local_ffmpeg not in os.environ.get("PATH", ""):
            os.environ["PATH"] = local_ffmpeg + os.pathsep + os.environ.get("PATH", "")

    def get_format_options(self, platform_key: str) -> List[FormatOption]:
        """Resolves FormatOption dataclass instances for the detected platform."""
        raw_list = SOCIAL_FORMAT_PROFILES if platform_key in ("facebook", "instagram", "tiktok", "twitter") else YOUTUBE_FORMAT_PROFILES
        return [FormatOption(**item) for item in raw_list]

    def run(self) -> int:
        """Main application lifecycle loop."""
        self.logger.info("=" * 60)
        self.logger.info(f"Video Downloader started (Python: {sys.version.split()[0]} | OS: {sys.platform})")

        while True:
            clear_terminal()
            BannerRenderer.render_header(self.console)

            # Check for candidate URL in clipboard
            clip_url = ClipboardHelper.get_media_url_candidate()
            BannerRenderer.render_input_prompt(self.console, clipboard_candidate=clip_url)

            raw_input = self.console.input(f"[bold {Theme.PRIMARY}]> [/]").strip()

            # If user pressed enter directly and clipboard candidate is present, use it
            if not raw_input and clip_url:
                url = clip_url
            elif not raw_input:
                continue
            else:
                url = raw_input

            url_cmd = url.lower()
            if url_cmd in ("q", "quit", "exit"):
                self.logger.info("User requested application exit.")
                ModalRenderer.render_goodbye_card(self.console)
                break
            elif url_cmd in ("cookies", "cookie", "auth"):
                ModalRenderer.show_cookies_modal(self.console)
                Prompt.ask("  Press Enter to return to main menu...")
                continue
            elif url_cmd in ("logs", "log"):
                view_recent_logs(self.console)
                Prompt.ask("  Press Enter to return to main menu...")
                continue
            elif url_cmd in ("help", "?"):
                ModalRenderer.show_help_modal(self.console)
                Prompt.ask("  Press Enter to return to main menu...")
                continue
            elif url_cmd in ("clear", "cls"):
                continue

            # Auto-prepend https:// if missing
            if not (url.startswith("http://") or url.startswith("https://")):
                if "." in url:
                    url = "https://" + url
                else:
                    self.logger.warning(f"Invalid URL entered: {url}")
                    self.console.print("\n  [bold red][ERROR][/bold red] Invalid URL entered. Please provide a valid media link.\n")
                    Prompt.ask("  Press Enter to try again...")
                    continue

            # Process the validated URL
            try:
                self.process_media(url)
            except KeyboardInterrupt:
                self.logger.warning("Download flow canceled by user.")
                self.console.print("\n  [bold yellow][ABORT][/bold yellow] Action canceled by user.\n")
                Prompt.ask("  Press Enter to return to main menu...")
            except Exception as e:
                self.logger.error(f"Unexpected error during download: {e}", exc_info=True)
                self.console.print(f"\n  [bold red][ERROR][/bold red] An unexpected error occurred: [dim]{e}[/dim]\n")
                Prompt.ask("  Press Enter to continue...")

        cleanup_terminal()
        return 0

    def process_media(self, url: str):
        """Coordinates metadata inspection, user selection, download execution, and post-action."""
        platform = PlatformDetector.detect(url)
        self.logger.info(f"Processing URL for platform '{platform.name}': {url}")
        self.console.print(f"\n  [bold {Theme.SUCCESS}]✓ Identified Platform:[/] {platform.badge}\n")

        # Step 1: Fetch and preview media metadata
        media = self.downloader.fetch_media_info(url)
        if not media:
            Prompt.ask("  Press Enter to continue...")
            return

        CardRenderer.render_media_card(self.console, media)

        # Step 2: Handle playlist detection for YouTube
        playlist_id = Sanitizer.extract_playlist_id(url)
        if playlist_id and ("v=" in url or "youtu.be/" in url):
            is_full_playlist, playlist_range = MenuRenderer.select_playlist_mode(self.console, media)
            media.is_playlist = is_full_playlist
            media.playlist_items_range = playlist_range
            if is_full_playlist:
                media.url = f"https://www.youtube.com/playlist?list={playlist_id}"
                # Refresh media info for the full playlist to obtain accurate title & video count
                playlist_info = self.downloader.fetch_media_info(media.url, cookies_from_browser=self.cookies_browser)
                if playlist_info:
                    media.title = playlist_info.title
                    media.playlist_count = playlist_info.playlist_count
                    media.duration = playlist_info.duration
                    media.raw_info = playlist_info.raw_info
            self.logger.info(f"Playlist mode selection: is_full_playlist={is_full_playlist}, range={playlist_range}")
        elif media.is_playlist:
            # Pure playlist link was provided
            playlist_range = MenuRenderer.prompt_playlist_range(self.console, media)
            media.playlist_items_range = playlist_range

        # Step 3: Interactive quality selection with estimated file sizes
        profiles = self.get_format_options(platform.key)
        selected_format_idx = MenuRenderer.interactive_format_menu(
            console=self.console,
            profiles=profiles,
            platform_name=platform.name,
            duration=media.duration,
            default_index=0,
        )
        chosen_profile = profiles[selected_format_idx]

        # Step 4: Storage destination
        dest_folder = os.path.join(DEFAULT_DOWNLOAD_DIR, platform.folder)
        os.makedirs(dest_folder, exist_ok=True)

        # Step 5: Pre-flight Summary Card
        CardRenderer.render_preflight_card(
            console=self.console,
            media=media,
            format_option=chosen_profile,
            dest_path=dest_folder,
        )

        # Step 6: Execute download with real-time progress engine
        result = self.downloader.execute_download(
            media=media,
            save_path=dest_folder,
            format_choice=selected_format_idx,
            cookies_from_browser=self.cookies_browser,
        )

        # Step 7: Download Result Dashboard
        if result.success:
            CardRenderer.render_success_card(self.console, result)
        else:
            CardRenderer.render_failure_card(self.console, result)

        # Step 8: Interactive Post-Download Action Menu with hotkeys
        target_dir = result.destination_path or dest_folder
        playable_file = None
        if result.success:
            candidate_files = result.completed_files + result.skipped_files
            for cand in candidate_files:
                cand_path = os.path.join(target_dir, cand)
                if os.path.isfile(cand_path):
                    playable_file = cand_path
                    break

            if not playable_file and os.path.isdir(target_dir):
                for f in sorted(os.listdir(target_dir)):
                    if any(f.endswith(ext) for ext in (".mp4", ".mkv", ".webm", ".mp3", ".m4a")):
                        playable_file = os.path.join(target_dir, f)
                        break

        while True:
            action_idx = MenuRenderer.interactive_post_download_menu(self.console, default_index=0)
            if action_idx == 0:  # Download another
                break
            elif action_idx == 1:  # Open folder
                SystemUtils.open_folder(target_dir)
            elif action_idx == 2:  # Play media
                if playable_file and os.path.isfile(playable_file):
                    SystemUtils.play_media(playable_file)
                else:
                    self.console.print("\n  [bold yellow]No newly downloaded media found to play.[/bold yellow]\n")
            elif action_idx == 3:  # View logs
                view_recent_logs(self.console)
                Prompt.ask("  Press Enter to return...")
            elif action_idx == 4:  # Exit
                ModalRenderer.render_goodbye_card(self.console)
                cleanup_terminal()
                sys.exit(0)
