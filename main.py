#!/usr/bin/env python3
"""
====================================================================
 Universal Media Downloader Pro (YouTube, Facebook & Social TUI)
 Next-Level Terminal TUI (Terminal User Interface)
 - Powered by yt-dlp and Rich
 - Multi-Platform Auto-Detection (YouTube, Facebook, Instagram, TikTok, X)
 - Interactive Arrow-Key & Direct Number Navigation (↑/↓, 1-5, Enter)
 - Instant Media Inspection & Metadata Preview Card
 - Smart Title Extraction & Clean Filename Sanitization
 - Lossless Video + Audio Merging via FFmpeg
 - Real-Time Rich Progress Engine (Speed, ETA, Downloaded/Total, Bar)
 - Dual-Bar Playlist Tracking & Smart Disk Auto-Resume
 - Optional Browser / Local Cookies Support for Private Media
====================================================================
"""

import os
import sys
import time
import shutil
import urllib.parse
import subprocess
import ctypes
import logging
import atexit
import signal
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any, List, Tuple

# Enable UTF-8 and ANSI colors / Virtual Terminal Processing on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    try:
        kernel32 = ctypes.windll.kernel32
        h_stdout = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        if kernel32.GetConsoleMode(h_stdout, ctypes.byref(mode)):
            kernel32.SetConsoleMode(h_stdout, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        pass

# Safe cross-platform terminal cleanup hook
def cleanup_terminal():
    """Guarantees cursor restoration and clean terminal buffer across Linux, macOS, and Windows."""
    try:
        sys.stdout.write("\033[?25h")  # Ensure cursor is visible
        sys.stdout.flush()
    except Exception:
        pass
    if sys.platform != "win32":
        try:
            import termios
            if sys.stdin.isatty():
                termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
        except Exception:
            pass

atexit.register(cleanup_terminal)

def _sigint_handler(sig, frame):
    cleanup_terminal()
    sys.exit(0)

try:
    signal.signal(signal.SIGINT, _sigint_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _sigint_handler)
except Exception:
    pass

# Ensure local ./ffmpeg/bin is added to PATH if present
_LOCAL_FFMPEG_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg", "bin")
if os.path.isdir(_LOCAL_FFMPEG_BIN) and _LOCAL_FFMPEG_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _LOCAL_FFMPEG_BIN + os.pathsep + os.environ.get("PATH", "")

# Verify essential packages
try:
    import yt_dlp
except ImportError:
    print("\n\033[91m[ERROR] 'yt-dlp' package is missing!\033[0m")
    launcher = "run.bat" if sys.platform == "win32" else "./run.sh"
    print(f"Please run '{launcher}' or install: pip install -U yt-dlp\n")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        DownloadColumn,
        TransferSpeedColumn,
        TimeRemainingColumn,
        TaskProgressColumn,
    )
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    from rich.prompt import Prompt
    from rich.rule import Rule
except ImportError:
    print("\n\033[91m[ERROR] 'rich' package is missing!\033[0m")
    launcher = "run.bat" if sys.platform == "win32" else "./run.sh"
    print(f"Please run '{launcher}' or install: pip install -r requirements.txt\n")
    sys.exit(1)

console = Console(highlight=False)

# Configure Production Application Logging with Rotation (3MB per file, 3 backups)
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube_downloader.log")

def setup_logger() -> logging.Logger:
    """Initializes dedicated rotating file logger with UTF-8 support."""
    logger = logging.getLogger("media_downloader")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=3 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

app_logger = setup_logger()


# ====================================================================
#  Cross-Platform Keyboard Input
# ====================================================================

def read_key() -> str:
    """
    Reads a single keypress across Windows and Linux/Unix.
    Returns: 'UP', 'DOWN', 'LEFT', 'RIGHT', 'ENTER', 'SPACE', 'ESC', 'CTRL_C', or character string.
    """
    if sys.platform == "win32":
        try:
            import msvcrt
            key = msvcrt.getch()
            if key in (b'\x00', b'\xe0'):
                sub_key = msvcrt.getch()
                if sub_key in (b'H', b'\x48'):
                    return "UP"
                elif sub_key in (b'P', b'\x50'):
                    return "DOWN"
                elif sub_key in (b'K', b'\x4b'):
                    return "LEFT"
                elif sub_key in (b'M', b'\x4d'):
                    return "RIGHT"
                return ""
            elif key == b'\x1b':
                if msvcrt.kbhit():
                    ch2 = msvcrt.getch()
                    if ch2 in (b'[', b'O'):
                        if msvcrt.kbhit():
                            ch3 = msvcrt.getch()
                            if ch3 == b'A':
                                return "UP"
                            elif ch3 == b'B':
                                return "DOWN"
                            elif ch3 == b'C':
                                return "RIGHT"
                            elif ch3 == b'D':
                                return "LEFT"
                return "ESC"
            elif key in (b'\r', b'\n'):
                return "ENTER"
            elif key == b' ':
                return "SPACE"
            elif key == b'\x03':
                return "CTRL_C"
            else:
                return key.decode("utf-8", errors="ignore")
        except Exception:
            return ""
    else:
        try:
            import tty
            import termios
            import select

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = os.read(fd, 1)
                if not ch:
                    return ""
                if ch == b'\x1b':
                    rlist, _, _ = select.select([fd], [], [], 0.05)
                    if rlist:
                        seq = os.read(fd, 8)
                        if not seq:
                            return "ESC"
                        if seq in (b'[', b'O'):
                            rlist2, _, _ = select.select([fd], [], [], 0.05)
                            if rlist2:
                                seq += os.read(fd, 8)
                        if seq.endswith(b'A') and (b'[' in seq or b'O' in seq):
                            return "UP"
                        elif seq.endswith(b'B') and (b'[' in seq or b'O' in seq):
                            return "DOWN"
                        elif seq.endswith(b'C') and (b'[' in seq or b'O' in seq):
                            return "RIGHT"
                        elif seq.endswith(b'D') and (b'[' in seq or b'O' in seq):
                            return "LEFT"
                        return ""
                    return "ESC"
                elif ch in (b'\r', b'\n'):
                    return "ENTER"
                elif ch == b' ':
                    return "SPACE"
                elif ch == b'\x03':
                    return "CTRL_C"
                else:
                    return ch.decode("utf-8", errors="ignore")
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:
            return ""


# ====================================================================
#  Format Configurations & Quality Profiles
# ====================================================================

YOUTUBE_FORMAT_PROFILES = [
    {
        "id": 0,
        "name": "Maximum Quality Video",
        "badge": "8K / 4K / 1080p60",
        "desc": "Lossless Video + Best Audio merged via FFmpeg (MP4)",
        "ext": "mp4",
        "tag": "ULTRA HD",
        "tag_color": "bright_cyan",
    },
    {
        "id": 1,
        "name": "1080p Full HD Video",
        "badge": "1080p Crisp",
        "desc": "Standard 1080p High-Definition MP4 (Optimal Compatibility)",
        "ext": "mp4",
        "tag": "FULL HD",
        "tag_color": "bright_green",
    },
    {
        "id": 2,
        "name": "720p HD Video",
        "badge": "720p Fast",
        "desc": "Fast download, compact file size, great for mobile (MP4)",
        "ext": "mp4",
        "tag": "COMPACT",
        "tag_color": "yellow",
    },
    {
        "id": 3,
        "name": "High-Fidelity Audio (MP3)",
        "badge": "320 kbps MP3",
        "desc": "Ultra high-bitrate studio audio extraction",
        "ext": "mp3",
        "tag": "AUDIO MP3",
        "tag_color": "bright_magenta",
    },
    {
        "id": 4,
        "name": "Original Audio (M4A)",
        "badge": "Best M4A / AAC",
        "desc": "Untouched original source audio stream",
        "ext": "m4a",
        "tag": "RAW AUDIO",
        "tag_color": "cyan",
    },
]

SOCIAL_FORMAT_PROFILES = [
    {
        "id": 0,
        "name": "Best Available Video (HD)",
        "badge": "HD / 1080p / Max",
        "desc": "Highest available resolution with best audio merged into MP4",
        "ext": "mp4",
        "tag": "BEST HD",
        "tag_color": "bright_cyan",
    },
    {
        "id": 1,
        "name": "High Definition (1080p / 720p)",
        "badge": "HD Crisp",
        "desc": "High-definition MP4 stream for fast download & crisp playback",
        "ext": "mp4",
        "tag": "HD MP4",
        "tag_color": "bright_green",
    },
    {
        "id": 2,
        "name": "Standard Definition (SD / 480p)",
        "badge": "SD 480p Compact",
        "desc": "Standard definition MP4, lightweight and great for sharing",
        "ext": "mp4",
        "tag": "SD COMPACT",
        "tag_color": "yellow",
    },
    {
        "id": 3,
        "name": "High-Fidelity Audio (MP3)",
        "badge": "320 kbps MP3",
        "desc": "Extract studio-quality 320kbps MP3 audio soundtrack",
        "ext": "mp3",
        "tag": "AUDIO MP3",
        "tag_color": "bright_magenta",
    },
    {
        "id": 4,
        "name": "Original Audio (M4A / AAC)",
        "badge": "Source Audio",
        "desc": "Untouched original audio stream directly from media",
        "ext": "m4a",
        "tag": "RAW AUDIO",
        "tag_color": "cyan",
    },
]

# Default profile set for backward compatibility
FORMAT_PROFILES = YOUTUBE_FORMAT_PROFILES


def get_format_profiles(platform_key: str) -> List[Dict[str, Any]]:
    """Returns platform-tailored format profiles."""
    if platform_key in ("facebook", "instagram", "tiktok", "twitter"):
        return SOCIAL_FORMAT_PROFILES
    return YOUTUBE_FORMAT_PROFILES


# ====================================================================
#  Helper Utilities
# ====================================================================

def format_duration(seconds: Any) -> str:
    """Formats seconds into human-readable duration (e.g. 03:45 or 1h 24m 10s). Safely handles floats and strings."""
    if not seconds:
        return "Unknown"
    try:
        total_sec = int(round(float(seconds)))
    except (ValueError, TypeError):
        return "Unknown"

    if total_sec <= 0:
        return "Unknown"

    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    secs = total_sec % 60
    if hours > 0:
        return f"{hours}h {minutes:02d}m {secs:02d}s"
    return f"{minutes:02d}:{secs:02d}"


def format_views(views: Any) -> str:
    """Formats view count with commas. Safely handles floats and strings."""
    if views is None:
        return "N/A"
    try:
        val = int(round(float(views)))
        return f"{val:,} views"
    except (ValueError, TypeError):
        views_str = str(views).strip()
        return "N/A" if not views_str else f"{views_str} views"


def format_file_size(bytes_val: Any) -> str:
    """Formats bytes into human-readable string (KB, MB, GB). Safely handles non-integers."""
    if not bytes_val:
        return "Unknown size"
    try:
        size = float(bytes_val)
    except (ValueError, TypeError):
        return "Unknown size"

    if size <= 0:
        return "Unknown size"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def extract_playlist_id(url: str) -> Optional[str]:
    """Extracts playlist ID from URL if present."""
    try:
        parsed = urllib.parse.urlparse(url)
        qs = urllib.parse.parse_qs(parsed.query)
        if "list" in qs and qs["list"]:
            return qs["list"][0]
    except Exception:
        pass
    return None


def is_ffmpeg_available() -> bool:
    """Checks if FFmpeg is available in system PATH or local directory."""
    return shutil.which("ffmpeg") is not None


def open_folder(folder_path: str):
    """Cross-platform folder opening in default file manager."""
    try:
        abs_path = os.path.abspath(folder_path)
        os.makedirs(abs_path, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(abs_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", abs_path])
        else:
            subprocess.Popen(["xdg-open", abs_path])
    except Exception as e:
        console.print(f"  [dim yellow]Notice: Could not open folder automatically ({e})[/dim yellow]\n")


def detect_platform(url: str) -> Dict[str, Any]:
    """
    Intelligently detects media platform from URL.
    Returns dictionary with platform key, display name, rich badge, folder name, and theme color.
    """
    url_lower = url.lower()
    if any(d in url_lower for d in ["facebook.com", "fb.watch", "fb.com", "fb.me"]):
        return {
            "key": "facebook",
            "name": "Facebook",
            "badge": "[bold white on blue] Facebook [/bold white on blue]",
            "color": "bright_blue",
            "icon": "🔵",
            "folder": "Facebook",
            "is_social": True,
        }
    elif any(d in url_lower for d in ["youtube.com", "youtu.be"]):
        return {
            "key": "youtube",
            "name": "YouTube",
            "badge": "[bold white on red] YouTube [/bold white on red]",
            "color": "bright_red",
            "icon": "🔴",
            "folder": "YouTube",
            "is_social": False,
        }
    elif any(d in url_lower for d in ["instagram.com", "instagr.am"]):
        return {
            "key": "instagram",
            "name": "Instagram",
            "badge": "[bold white on magenta] Instagram [/bold white on magenta]",
            "color": "bright_magenta",
            "icon": "🟣",
            "folder": "Instagram",
            "is_social": True,
        }
    elif "tiktok.com" in url_lower:
        return {
            "key": "tiktok",
            "name": "TikTok",
            "badge": "[bold white on black] TikTok [/bold white on black]",
            "color": "bright_white",
            "icon": "⬛",
            "folder": "TikTok",
            "is_social": True,
        }
    elif any(d in url_lower for d in ["twitter.com", "x.com"]):
        return {
            "key": "twitter",
            "name": "Twitter / X",
            "badge": "[bold white on cyan] Twitter/X [/bold white on cyan]",
            "color": "bright_cyan",
            "icon": "🐦",
            "folder": "Twitter",
            "is_social": True,
        }
    else:
        return {
            "key": "generic",
            "name": "Web Media",
            "badge": "[bold white on green] Web Media [/bold white on green]",
            "color": "bright_green",
            "icon": "🌐",
            "folder": "WebMedia",
            "is_social": False,
        }


def clean_media_title(info: Dict[str, Any], platform_key: str) -> str:
    """
    Intelligently cleans and resolves human-readable titles.
    For Facebook/Instagram posts where 'title' is missing or numeric, falls back to caption snippet or creator.
    """
    title = (info.get("title") or "").strip()
    desc = (info.get("description") or "").strip()
    uploader = (info.get("uploader") or info.get("channel") or info.get("uploader_id") or "").strip()

    is_generic = False
    if not title:
        is_generic = True
    elif platform_key == "facebook":
        title_lower = title.lower()
        if "facebook video" in title_lower or title_lower.isdigit() or len(title_lower) < 4:
            is_generic = True

    if is_generic and desc:
        lines = [line.strip() for line in desc.splitlines() if line.strip()]
        if lines:
            first_line = lines[0]
            if len(first_line) > 60:
                first_line = first_line[:57] + "..."
            if uploader and uploader not in first_line:
                title = f"{uploader} - {first_line}"
            else:
                title = first_line

    if not title:
        if uploader:
            title = f"{uploader} - {info.get('id', 'Media')}"
        else:
            title = f"Media_{info.get('id', 'video')}"

    # Strip dangerous filename characters for Linux / Windows / macOS
    cleaned = "".join(c for c in title if c not in r'\/:*?"<>|' and ord(c) >= 32).strip()

    # Enforce cross-platform safe filename length (max 80 chars / 180 bytes in UTF-8)
    if len(cleaned.encode("utf-8", errors="ignore")) > 180:
        cleaned = cleaned[:60] + "..."

    return cleaned or "Media_Download"


# ====================================================================
#  UI Rendering Components
# ====================================================================

def render_header():
    """Renders the top application banner and system status badges with next-level styling."""
    ffmpeg_ready = is_ffmpeg_available()
    ffmpeg_st = "[bold green]Ready[/bold green]" if ffmpeg_ready else "[bold yellow]Missing[/bold yellow]"
    os_name = "Windows" if sys.platform == "win32" else ("macOS" if sys.platform == "darwin" else "Linux")

    cookies_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
    cookies_present = os.path.isfile(cookies_file)
    cookies_st = "[bold green]cookies.txt[/bold green]" if cookies_present else "[dim]Default[/dim]"

    content = Table.grid(expand=True)
    content.add_column(justify="center")

    # 1. Hero Brand Title
    title = Text.from_markup(
        "[bold bright_yellow]⚡[/bold bright_yellow] "
        "[bold bright_white]UNIVERSAL[/bold bright_white] "
        "[bold bright_cyan]MEDIA DOWNLOADER[/bold bright_cyan] "
        "[bold black on bright_yellow] PRO [/bold black on bright_yellow] "
        "[bold dim white]v3.5[/bold dim white]"
    )
    sub = Text.from_markup("[dim cyan]Lossless 8K / 4K / HD Video & 320kbps Audio Merging Engine[/dim cyan]")

    # 2. Supported Platforms Ribbon
    platforms = Text.from_markup(
        "[bold white on #e50914] ▶ YouTube [/]  "
        "[bold white on #1877f2] f Facebook [/]  "
        "[bold white on #c13584] 📷 Instagram [/]  "
        "[bold white on #010101] 🎵 TikTok [/]  "
        "[bold white on #1da1f2] 𝕏 Twitter [/]"
    )

    # 3. System Specs Line (Clean, guaranteed single-line fit on 80-col)
    status_line = Text.from_markup(
        f"[dim]Engine:[/dim] [cyan]yt-dlp[/cyan]   │   "
        f"[dim]FFmpeg:[/dim] {ffmpeg_st}   │   "
        f"[dim]OS:[/dim] [bright_white]{os_name}[/bright_white]   │   "
        f"[dim]Auth:[/dim] {cookies_st}"
    )

    content.add_row(title)
    content.add_row(sub)
    content.add_row(Text(""))
    content.add_row(platforms)
    content.add_row(Text("─" * 68, style="dim #1e293b"))
    content.add_row(status_line)

    banner = Panel(
        content,
        border_style="bright_cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(banner)
    console.print()


def render_input_prompt_card():
    """Renders an interactive, styled prompt card for URL input."""
    content = Table.grid(expand=True)
    content.add_column(justify="left")

    line1 = Text.from_markup("[bold bright_white]📥 Paste Media Link (Video, Reel, Short or Playlist):[/bold bright_white]")
    line2 = Text.from_markup("[dim]Keys: [/dim][bold bright_red]q[/bold bright_red][dim]=Quit  •  [/dim][bold yellow]cookies[/bold yellow][dim]=Auth Help  •  [/dim][bold cyan]logs[/bold cyan][dim]=View Log  •  [/dim][bold magenta]help[/bold magenta][dim]=Guide[/dim]")

    content.add_row(line1)
    content.add_row(line2)

    prompt_panel = Panel(
        content,
        border_style="cyan",
        box=box.ROUNDED,
        padding=(0, 2),
    )
    console.print(prompt_panel)


def show_cookies_modal():
    """Displays an interactive modal guiding the user on how to use cookies.txt."""
    cookies_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
    has_cookies = os.path.isfile(cookies_path)

    grid = Table.grid(padding=(0, 1), expand=True)
    grid.add_column()

    status_text = "[bold bright_green]✓ Active & Loaded[/bold bright_green]" if has_cookies else "[bold yellow]● Not Found (Public mode active)[/bold yellow]"

    grid.add_row(Text.from_markup(f"[bold cyan]Current Status:[/bold cyan] {status_text}"))
    grid.add_row(Text.from_markup(f"[dim]Expected Location: {cookies_path}[/dim]\n"))

    grid.add_row(Text.from_markup("[bold bright_white]Why do you need cookies.txt?[/bold bright_white]"))
    grid.add_row(Text.from_markup("• Download [bold blue]private Facebook group videos[/bold blue] or friends-only posts."))
    grid.add_row(Text.from_markup("• Download [bold magenta]restricted Instagram reels[/bold magenta] and follower-only media."))
    grid.add_row(Text.from_markup("• Bypass [bold red]YouTube age-restrictions[/bold red] or member-only videos.\n"))

    grid.add_row(Text.from_markup("[bold bright_white]How to set up in 2 minutes:[/bold bright_white]"))
    grid.add_row(Text.from_markup("1. Install a browser extension (e.g. [bold cyan]Get cookies.txt LOCALLY[/bold cyan])."))
    grid.add_row(Text.from_markup("2. Open Facebook / YouTube in your browser while logged in."))
    grid.add_row(Text.from_markup("3. Export cookies and save the file as [bold bright_yellow]cookies.txt[/bold bright_yellow] in this project folder."))
    grid.add_row(Text.from_markup("4. The engine will automatically authenticate all restricted downloads!"))

    panel = Panel(
        grid,
        title="[bold bright_yellow] 🍪 Cookie Authentication Guide [/bold bright_yellow]",
        border_style="yellow",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


def show_help_modal():
    """Displays an interactive quick reference guide."""
    grid = Table.grid(padding=(0, 1), expand=True)
    grid.add_column()

    grid.add_row(Text.from_markup("[bold bright_white]⚡ Key Commands & Shortcuts:[/bold bright_white]"))
    grid.add_row(Text.from_markup("  [bold red]q[/bold red]            : Exit application immediately."))
    grid.add_row(Text.from_markup("  [bold yellow]cookies[/bold yellow]      : View cookies.txt status & setup instructions."))
    grid.add_row(Text.from_markup("  [bold cyan]logs[/bold cyan]         : Open and inspect download logs in terminal."))
    grid.add_row(Text.from_markup("  [bold green]clear[/bold green]        : Clear screen and refresh dashboard."))
    grid.add_row(Text.from_markup("  [bold white]Ctrl + C[/bold white]     : Safely cancel current action or download.\n"))

    grid.add_row(Text.from_markup("[bold bright_white]🎯 Navigation & Quality:[/bold bright_white]"))
    grid.add_row(Text.from_markup("  • Use [bold cyan]↑ / ↓[/bold cyan] arrow keys or numbers [bold cyan]1-5[/bold cyan] to select format quality."))
    grid.add_row(Text.from_markup("  • Press [bold cyan]Enter[/bold cyan] to confirm selection and start lossless merge."))
    grid.add_row(Text.from_markup("  • Download folders are auto-sorted into [bold cyan]downloads/<Platform>/[/bold cyan]."))

    panel = Panel(
        grid,
        title="[bold bright_cyan] 💡 Quick Reference & Help [/bold bright_cyan]",
        border_style="bright_cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


def render_goodbye_card():
    """Displays a clean exit panel upon quit."""
    content = Table.grid(expand=True)
    content.add_column(justify="center")
    content.add_row(Text.from_markup("[bold bright_cyan]⚡ Thank you for using Universal Media Downloader Pro![/bold bright_cyan]"))
    content.add_row(Text.from_markup("[dim]All downloads are safely stored in your project's downloads/ directory.[/dim]"))
    panel = Panel(
        content,
        border_style="bright_cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


def fetch_media_info(url: str, cookies_from_browser: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Fetches media title, uploader, duration, and playlist count with a live spinner."""
    platform = detect_platform(url)
    cookies_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")

    ydl_opts = {
        "extract_flat": "in_playlist",
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    if os.path.isfile(cookies_file):
        ydl_opts["cookiefile"] = cookies_file
        app_logger.info(f"Using local cookies.txt from: {cookies_file}")
    elif cookies_from_browser:
        ydl_opts["cookiesfrombrowser"] = (cookies_from_browser, None, None, None)
        app_logger.info(f"Using browser cookies from: {cookies_from_browser}")

    with console.status(f"[bold cyan]⠋ Fetching media information from {platform['name']}...", spinner="dots"):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    return None
                return info
        except Exception as e:
            err_msg = str(e)
            console.print(f"\n  [bold red][ERROR][/bold red] Could not fetch media info: [dim]{err_msg}[/dim]\n")
            if any(term in err_msg.lower() for term in ("login", "sign in", "private", "account", "cookies", "restricted")):
                console.print("  [bold yellow]💡 Authentication / Cookie Tip:[/bold yellow]")
                console.print("  This video might be private, friends-only, or requires Facebook/Instagram login.")
                console.print("  To download private videos, place an exported [bold white]cookies.txt[/bold white] file in:")
                console.print(f"  [cyan]{os.path.dirname(os.path.abspath(__file__))}/cookies.txt[/cyan]\n")
            return None


def render_media_card(info: Dict[str, Any], url: str, platform: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
    """
    Renders a visual card of the detected media.
    Returns (is_playlist, resolved_clean_title).
    """
    platform = platform or detect_platform(url)
    is_playlist = info.get("_type") == "playlist" or "entries" in info
    title = clean_media_title(info, platform["key"])
    uploader = info.get("uploader") or info.get("channel") or info.get("uploader_id") or "Various / Unknown"

    table = Table.grid(padding=(0, 2))
    table.add_column("Key", style="bold cyan", justify="right", width=12)
    table.add_column("Value", style="white")

    table.add_row("Platform:", f"{platform['badge']}")
    table.add_row("Title:", f"[bold bright_white]{title}[/bold bright_white]")
    table.add_row("Author/Page:", f"[bright_yellow]{uploader}[/bright_yellow]")

    if is_playlist:
        entries = list(info.get("entries") or [])
        count = len(entries) if entries else (info.get("playlist_count") or "Unknown")
        table.add_row("Content:", f"[bold bright_magenta]Playlist / Collection ({count} items)[/bold bright_magenta]")
    else:
        duration = format_duration(info.get("duration"))
        views = format_views(info.get("view_count"))
        table.add_row("Duration:", f"[bright_green]{duration}[/bright_green]")
        if views != "N/A":
            table.add_row("Views:", f"[bright_white]{views}[/bright_white]")
        table.add_row("Content:", f"[bold bright_cyan]{platform['name']} Media[/bold bright_cyan]")

    table.add_row("Source URL:", f"[dim]{url[:70] + ('...' if len(url) > 70 else '')}[/dim]")

    border_color = platform["color"] if platform["color"] in ("cyan", "green", "magenta", "yellow", "blue", "red") else "cyan"
    panel = Panel(
        table,
        title=f"[bold bright_white] {platform['icon']} Media Information [/bold bright_white]",
        border_style=border_color,
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()
    return is_playlist, title


def generate_format_menu_table(
    selected_index: int,
    profiles: Optional[List[Dict[str, Any]]] = None,
    platform_name: str = "Media",
) -> Panel:
    """Constructs the styled format table for the interactive menu."""
    profiles = profiles or FORMAT_PROFILES
    table = Table(show_header=True, header_style="bold bright_white", box=None, padding=(0, 1), expand=True)
    table.add_column("Key", width=6, justify="center")
    table.add_column("Quality & Format", width=30)
    table.add_column("Tag", width=14, justify="center")
    table.add_column("Description", style="dim")

    for idx, prof in enumerate(profiles):
        num = idx + 1
        tag = f"[{prof['tag_color']}][{prof['tag']}][/{prof['tag_color']}]"

        if idx == selected_index:
            table.add_row(
                f"[bold bright_cyan]> [{num}][/bold bright_cyan]",
                f"[bold bright_white]{prof['name']}[/bold bright_white]",
                tag,
                f"[bright_white]{prof['desc']}[/bright_white]",
            )
        else:
            table.add_row(
                f"  [dim][{num}][/dim]",
                f"[dim]{prof['name']}[/dim]",
                f"[dim]{prof['tag']}[/dim]",
                f"[dim]{prof['desc']}[/dim]",
            )

    return Panel(
        table,
        title=f"[bold bright_cyan] Select Quality & Format ({platform_name}) [/bold bright_cyan]",
        subtitle=f"[dim]Use Up/Down arrows or keys 1-{len(profiles)}, Enter to confirm[/dim]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 1),
    )


def interactive_format_menu(
    profiles: Optional[List[Dict[str, Any]]] = None,
    default_index: int = 0,
    platform_name: str = "Media",
) -> int:
    """
    Renders an interactive selection menu with Arrow Key Navigation and direct 1-5 keypresses.
    Falls back gracefully to numeric input if not in a TTY.
    """
    profiles = profiles or FORMAT_PROFILES
    num_options = len(profiles)
    selected = min(default_index, num_options - 1)

    # Fallback for non-interactive TTY environments
    if not sys.stdin.isatty():
        console.print(generate_format_menu_table(selected, profiles, platform_name))
        choice = Prompt.ask(
            "  Select format",
            choices=[str(i + 1) for i in range(num_options)],
            default="1",
        )
        return int(choice) - 1

    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        with Live(generate_format_menu_table(selected, profiles, platform_name), console=console, auto_refresh=False) as live:
            while True:
                key = read_key()

                if key in ("UP", "k", "K", "w", "W"):
                    selected = (selected - 1) % num_options
                    live.update(generate_format_menu_table(selected, profiles, platform_name), refresh=True)
                elif key in ("DOWN", "j", "J", "s", "S"):
                    selected = (selected + 1) % num_options
                    live.update(generate_format_menu_table(selected, profiles, platform_name), refresh=True)
                elif key.isdigit() and 1 <= int(key) <= num_options:
                    selected = int(key) - 1
                    live.update(generate_format_menu_table(selected, profiles, platform_name), refresh=True)
                    break
                elif key in ("ENTER", "SPACE"):
                    break
                elif key in ("ESC", "q", "Q"):
                    break
                elif key == "CTRL_C":
                    raise KeyboardInterrupt
    finally:
        # Restore cursor
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        if sys.platform != "win32":
            try:
                import termios
                termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
            except Exception:
                pass

    chosen = profiles[selected]
    console.print(f"  [bold bright_green]✓ Selected:[/bold bright_green] [bold white]{chosen['name']}[/bold white] [dim]({chosen['desc']})[/dim]\n")
    return selected


def select_playlist_mode(info: Dict[str, Any], url: str) -> bool:
    """
    When a URL contains both an individual video and a playlist,
    asks the user whether to download the single video or the full playlist.
    """
    options = [
        "Download Entire Playlist (Auto-skips existing files)",
        "Download Only This Single Video",
    ]
    selected = 0

    if not sys.stdin.isatty():
        choice = Prompt.ask(
            "  Playlist & Video detected. Choose mode",
            choices=["1", "2"],
            default="1",
        )
        return choice == "1"

    def get_panel(sel: int):
        table = Table.grid(padding=(0, 2))
        table.add_column("Key", width=6)
        table.add_column("Option", style="white")

        for idx, opt in enumerate(options):
            num = idx + 1
            if idx == sel:
                table.add_row(f"[bold bright_cyan]> [{num}][/bold bright_cyan]", f"[bold bright_white]{opt}[/bold bright_white]")
            else:
                table.add_row(f"  [dim][{num}][/dim]", f"[dim]{opt}[/dim]")

        return Panel(
            table,
            title="[bold yellow] Video in Playlist Detected [/bold yellow]",
            subtitle="[dim]Use Up/Down arrows or 1-2, Enter to confirm[/dim]",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(1, 2),
        )

    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        with Live(get_panel(selected), console=console, auto_refresh=False) as live:
            while True:
                key = read_key()
                if key in ("UP", "DOWN", "k", "j"):
                    selected = 1 - selected
                    live.update(get_panel(selected), refresh=True)
                elif key in ("1", "2"):
                    selected = int(key) - 1
                    live.update(get_panel(selected), refresh=True)
                    break
                elif key in ("ENTER", "SPACE"):
                    break
                elif key == "CTRL_C":
                    raise KeyboardInterrupt
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    console.print(f"  [bold bright_green]✓ Mode:[/bold bright_green] [bold white]{options[selected]}[/bold white]\n")
    return selected == 0


def render_preflight_card(
    title: str,
    format_name: str,
    destination_path: str,
    is_playlist: bool,
    playlist_count: Optional[int] = None,
    platform: Optional[Dict[str, Any]] = None,
):
    """Renders the pre-download confirmation summary card."""
    table = Table.grid(padding=(0, 2))
    table.add_column("Key", style="bold cyan", justify="right", width=14)
    table.add_column("Value", style="white")

    if platform:
        table.add_row("Platform:", f"{platform['badge']}")
    table.add_row("Target:", f"[bold bright_white]{title}[/bold bright_white]")
    table.add_row("Profile:", f"[bright_yellow]{format_name}[/bright_yellow]")
    table.add_row("Destination:", f"[bright_cyan]{destination_path}[/bright_cyan]")
    if is_playlist:
        table.add_row("Playlist Items:", f"[bright_magenta]{playlist_count or 'Multiple'} items[/bright_magenta]")
    table.add_row("Smart Resume:", "[bright_green]Active (.part files will resume seamlessly)[/bright_green]")
    table.add_row("Disk Check:", "[bright_green]Active (Existing files > 1KB will be skipped)[/bright_green]")

    panel = Panel(
        table,
        title="[bold bright_cyan] Pre-Download Summary [/bold bright_cyan]",
        border_style="bright_cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print(panel)
    console.print()


def render_success_card(
    title: str,
    destination_path: str,
    elapsed_str: str,
    is_playlist: bool,
    completed_items: Optional[List[Dict[str, Any]]] = None,
    skipped_items: Optional[List[Dict[str, Any]]] = None,
    platform: Optional[Dict[str, Any]] = None,
):
    """Renders the success dashboard upon download completion."""
    completed_items = completed_items or []
    skipped_items = skipped_items or []
    num_completed = len(completed_items)
    num_skipped = len(skipped_items)

    if num_completed == 0 and num_skipped == 0:
        table = Table.grid(padding=(0, 2))
        table.add_column("Key", style="bold red", justify="right", width=14)
        table.add_column("Value", style="white")

        if platform:
            table.add_row("Platform:", f"{platform['badge']}")
        table.add_row("Status:", "[bold red]No Media Downloaded (0 files saved)[/bold red]")
        table.add_row("Target:", f"[bold bright_white]{title}[/bold bright_white]")
        table.add_row("Destination:", f"[bright_cyan]{destination_path}[/bright_cyan]")
        table.add_row("Time Taken:", f"[bright_white]{elapsed_str}[/bright_white]")
        table.add_row("Log File:", f"[bright_magenta]{LOG_FILE}[/bright_magenta]")

        panel = Panel(
            table,
            title="[bold red] Download Incomplete / Check Log [/bold red]",
            border_style="red",
            box=box.ROUNDED,
            padding=(1, 2),
        )
        console.print()
        console.print(panel)
        console.print("  [bold yellow]💡 Tip:[/bold yellow] Inspect recent logs (Option 3 in the menu below) to see details, or check video permissions.\n")
        return

    table = Table.grid(padding=(0, 2))
    table.add_column("Key", style="bold bright_green", justify="right", width=14)
    table.add_column("Value", style="white")

    status_str = f"[bold bright_green]Completed Successfully ({num_completed} downloaded)[/bold bright_green]"
    if num_skipped > 0:
        status_str += f"  [dim yellow]({num_skipped} already on disk / skipped)[/dim yellow]"

    if platform:
        table.add_row("Platform:", f"{platform['badge']}")
    table.add_row("Status:", status_str)
    table.add_row("Media:", f"[bold bright_white]{title}[/bold bright_white]")
    table.add_row("Saved in:", f"[bright_cyan]{destination_path}[/bright_cyan]")
    table.add_row("Time Taken:", f"[bright_white]{elapsed_str}[/bright_white]")
    table.add_row("Log File:", f"[bright_magenta]{LOG_FILE}[/bright_magenta]")

    panel = Panel(
        table,
        title="[bold bright_green] Download Complete [/bold bright_green]",
        border_style="bright_green",
        box=box.ROUNDED,
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()

    # Detailed item breakdown table
    if completed_items or skipped_items:
        item_table = Table(
            box=box.ROUNDED,
            show_header=True,
            header_style="bold bright_cyan",
            expand=True,
            padding=(0, 1),
        )
        item_table.add_column("#", width=4, justify="center")
        item_table.add_column("Status", width=16)
        item_table.add_column("File Name", style="bold bright_white")
        item_table.add_column("Size", width=14, justify="right", style="bright_green")

        row_idx = 1
        for itm in completed_items:
            item_table.add_row(
                str(row_idx),
                "[bold bright_green]✓ Completed[/bold bright_green]",
                itm.get("name", "Unknown"),
                itm.get("size", "Completed"),
            )
            row_idx += 1

        for itm in skipped_items:
            item_table.add_row(
                str(row_idx),
                "[bold yellow]⚡ Skipped[/bold yellow]",
                itm.get("name", "Unknown"),
                f"[dim]{itm.get('size', 'Exists')}[/dim]",
            )
            row_idx += 1

        summary_panel = Panel(
            item_table,
            title="[bold bright_cyan] Downloaded Items Summary [/bold bright_cyan]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 1),
        )
        console.print(summary_panel)
        console.print()


# ====================================================================
#  Smart Disk Check Filter (Auto-Skip Existing Media)
# ====================================================================

def make_disk_check_filter(ydl, format_choice: int, is_playlist: bool = False, on_skip=None):
    """
    Inspects the disk before downloading:
    - If the video/audio file is already present on disk (> 1KB, not .part/.ytdl), skips download.
    - If incomplete (.part), proceeds to resume seamlessly.
    """
    if format_choice in (3, 4):
        valid_exts = {".mp3", ".m4a", ".opus", ".aac", ".flac", ".wav", ".ogg"}
    else:
        valid_exts = {".mp4", ".mkv", ".webm", ".avi", ".mov", ".ts"}

    def disk_check_filter(info_dict, *, incomplete=False):
        try:
            target = ydl.prepare_filename(info_dict)
            dir_name = os.path.dirname(target)
            if not os.path.isdir(dir_name):
                return None

            base, _ = os.path.splitext(target)

            # 1. Check exact base filename with valid media extensions
            for ext in valid_exts:
                cand = base + ext
                if os.path.isfile(cand) and os.path.getsize(cand) > 1024 and not cand.endswith(".part") and not cand.endswith(".ytdl"):
                    fname = os.path.basename(cand)
                    fsize = format_file_size(os.path.getsize(cand))
                    if on_skip:
                        on_skip(fname, fsize, cand)
                    return f"Skipping '{fname}': already exists on disk"

            # 2. For playlist videos, check by numbered index prefix (e.g. '01 - ')
            index = info_dict.get("playlist_index")
            if is_playlist and index is not None:
                try:
                    prefix = f"{int(index):02d} - "
                    for f in os.listdir(dir_name):
                        if f.startswith(prefix) and any(f.endswith(e) for e in valid_exts):
                            full = os.path.join(dir_name, f)
                            if os.path.isfile(full) and os.path.getsize(full) > 1024 and not f.endswith(".part") and not f.endswith(".ytdl"):
                                fsize = format_file_size(os.path.getsize(full))
                                if on_skip:
                                    on_skip(f, fsize, full)
                                return f"Skipping '{f}': already exists on disk"
                except Exception:
                    pass
        except Exception:
            pass

        return None

    return disk_check_filter


# ====================================================================
#  yt-dlp Configuration Factory & File Logger Bridge
# ====================================================================

class YtDlpLogger:
    """Redirects yt-dlp internal messages to the log file while keeping terminal clean."""
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def debug(self, msg: str):
        if msg and msg.strip():
            self.logger.debug(f"[yt-dlp] {msg.strip()}")

    def info(self, msg: str):
        if msg and msg.strip():
            self.logger.info(f"[yt-dlp] {msg.strip()}")

    def warning(self, msg: str):
        if msg and msg.strip():
            self.logger.warning(f"[yt-dlp] {msg.strip()}")

    def error(self, msg: str):
        if msg and msg.strip():
            self.logger.error(f"[yt-dlp] {msg.strip()}")


def build_ydl_options(
    save_path: str,
    format_choice: int,
    is_playlist: bool,
    progress_hooks: list,
    postprocessor_hooks: list,
    post_hooks: list,
    platform_key: str = "generic",
    cookies_file: Optional[str] = None,
    cookies_from_browser: Optional[str] = None,
) -> dict:
    """Builds the comprehensive yt-dlp parameters."""
    os.makedirs(save_path, exist_ok=True)

    if is_playlist:
        out_template = os.path.join(
            save_path,
            "%(playlist_title|Playlist)s",
            "%(playlist_index&{:02d} - |)s%(title,id)s.%(ext)s",
        )
    else:
        out_template = os.path.join(save_path, "%(title,id)s.%(ext)s")

    ydl_opts = {
        "outtmpl": {"default": out_template},
        "windowsfilenames": True,
        "trim_file_name": 100,
        "ignoreerrors": True,
        "retries": 10,
        "fragment_retries": 10,
        "concurrent_fragment_downloads": 5,
        "progress_hooks": progress_hooks,
        "postprocessor_hooks": postprocessor_hooks,
        "post_hooks": post_hooks,
        "continuedl": True,
        "nooverwrites": True,
        "noplaylist": not is_playlist,
        "logger": YtDlpLogger(app_logger),
        "noprogress": True,
        "quiet": True,
        "no_warnings": True,
    }

    if cookies_file and os.path.isfile(cookies_file):
        ydl_opts["cookiefile"] = cookies_file
    elif cookies_from_browser:
        ydl_opts["cookiesfrombrowser"] = (cookies_from_browser, None, None, None)

    # Format choices mapping:
    # 0 -> Maximum Quality (8K/4K/1080p on YouTube, Best HD on Facebook/Social)
    # 1 -> 1080p Full HD Video (MP4)
    # 2 -> 720p HD Video on YouTube, 480p SD on Social
    # 3 -> Audio Only (320kbps MP3)
    # 4 -> Audio Only (Best Original / M4A)

    if platform_key in ("facebook", "instagram", "tiktok", "twitter"):
        if format_choice == 0:
            ydl_opts.update({
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
                "final_ext": "mp4",
            })
        elif format_choice == 1:
            ydl_opts.update({
                "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
                "merge_output_format": "mp4",
                "final_ext": "mp4",
            })
        elif format_choice == 2:
            ydl_opts.update({
                "format": "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
                "merge_output_format": "mp4",
                "final_ext": "mp4",
            })
        elif format_choice == 3:
            ydl_opts.update({
                "format": "bestaudio/best",
                "final_ext": "mp3",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "320",
                    }
                ],
            })
        elif format_choice == 4:
            ydl_opts.update({
                "format": "bestaudio/best",
                "final_ext": "m4a",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "m4a",
                    }
                ],
            })
    else:
        # YouTube & Standard Web Media
        if format_choice == 0:
            ydl_opts.update({
                "format": "bestvideo+bestaudio/best",
                "format_sort": ["res", "fps", "hdr:12", "vcodec", "channels", "br", "asr"],
                "merge_output_format": "mp4",
                "final_ext": "mp4",
            })
        elif format_choice == 1:
            ydl_opts.update({
                "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
                "merge_output_format": "mp4",
                "final_ext": "mp4",
            })
        elif format_choice == 2:
            ydl_opts.update({
                "format": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
                "merge_output_format": "mp4",
                "final_ext": "mp4",
            })
        elif format_choice == 3:
            ydl_opts.update({
                "format": "bestaudio/best",
                "final_ext": "mp3",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "320",
                    }
                ],
            })
        elif format_choice == 4:
            ydl_opts.update({
                "format": "bestaudio/best",
                "final_ext": "m4a",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "m4a",
                    }
                ],
            })

    return ydl_opts


# ====================================================================
#  Download Execution & Real-Time Progress Engine
# ====================================================================

def run_download(
    url: str,
    save_path: str,
    format_choice: int,
    is_playlist: bool,
    total_videos: Optional[int] = None,
    platform_key: str = "generic",
    cookies_file: Optional[str] = None,
    cookies_from_browser: Optional[str] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """Executes the download with the Rich Progress Engine."""
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold bright_cyan]{task.description}"),
        BarColumn(bar_width=26, complete_style="bright_cyan", finished_style="bright_green"),
        TaskProgressColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False,
    )

    playlist_task_id = None
    stream_task_id = None
    completed_items: List[Dict[str, Any]] = []
    skipped_items: List[Dict[str, Any]] = []
    processed_count = 0

    def on_skip_callback(fname: str, fsize: str, fpath: str):
        nonlocal processed_count
        processed_count += 1
        skipped_items.append({"name": fname, "size": fsize, "path": fpath, "status": "Skipped (Exists)"})
        app_logger.info(f"[SKIPPED] Already exists on disk: '{fname}' ({fsize}) at '{fpath}'")

        if is_playlist and total_videos and total_videos > 1:
            progress.console.print(
                f"  [bold yellow]⚡ Skipped ({processed_count}/{total_videos}):[/bold yellow] [bright_white]{fname}[/bright_white] [dim]({fsize} - already exists)[/dim]"
            )
            if playlist_task_id is not None:
                progress.advance(playlist_task_id, 1)
        else:
            progress.console.print(
                f"  [bold yellow]⚡ Skipped:[/bold yellow] [bright_white]{fname}[/bright_white] [dim]({fsize} - already exists)[/dim]"
            )

    def post_hook_callback(filepath: str):
        nonlocal stream_task_id, processed_count
        processed_count += 1
        fname = os.path.basename(filepath) if filepath else "Media"
        fsize = format_file_size(os.path.getsize(filepath)) if filepath and os.path.isfile(filepath) else "Completed"
        completed_items.append({"name": fname, "size": fsize, "path": filepath, "status": "Completed"})
        app_logger.info(f"[COMPLETED] Download finished: '{fname}' | Size: {fsize} | Path: '{filepath}'")

        # Clean up stream progress bar for next video
        if stream_task_id is not None:
            try:
                progress.remove_task(stream_task_id)
            except Exception:
                pass
            stream_task_id = None

        if is_playlist and total_videos and total_videos > 1:
            progress.console.print(
                f"  [bold bright_green]✓ Completed ({processed_count}/{total_videos}):[/bold bright_green] [bold bright_white]{fname}[/bold bright_white] [bold bright_green]({fsize})[/bold bright_green]"
            )
            if playlist_task_id is not None:
                progress.advance(playlist_task_id, 1)
        else:
            progress.console.print(
                f"  [bold bright_green]✓ Completed:[/bold bright_green] [bold bright_white]{fname}[/bold bright_white] [bold bright_green]({fsize})[/bold bright_green]"
            )

    def progress_hook(d):
        nonlocal stream_task_id
        status = d.get("status")

        if status == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            info = d.get("info_dict", {})
            vcodec = info.get("vcodec")
            acodec = info.get("acodec")

            # Label whether this stream is video or audio
            if vcodec is not None and vcodec != "none" and (acodec is None or acodec == "none"):
                stream_type = "Video Stream"
            elif acodec is not None and acodec != "none" and (vcodec is None or vcodec == "none"):
                stream_type = "Audio Stream"
            else:
                stream_type = "Media Stream"

            fname = os.path.basename(d.get("filename", "Media"))
            short_name = fname[:24] + "..." if len(fname) > 24 else fname

            if stream_task_id is None:
                stream_task_id = progress.add_task(f"Downloading {stream_type} ({short_name})", total=total, completed=downloaded)
            else:
                progress.update(
                    stream_task_id,
                    description=f"Downloading {stream_type} ({short_name})",
                    completed=downloaded,
                    total=total,
                )

        elif status == "finished":
            if stream_task_id is not None:
                progress.update(stream_task_id, description="[bold bright_green]Stream download finished[/bold bright_green]")

    def postprocessor_hook(d):
        nonlocal stream_task_id
        status = d.get("status")

        if status == "started":
            if stream_task_id is not None:
                progress.update(stream_task_id, description="[bold bright_yellow]⚡ Merging streams with FFmpeg...[/bold bright_yellow]")
        elif status == "finished":
            if stream_task_id is not None:
                progress.update(stream_task_id, description="[bold bright_green]✓ Lossless merge completed[/bold bright_green]")

    ydl_opts = build_ydl_options(
        save_path=save_path,
        format_choice=format_choice,
        is_playlist=is_playlist,
        progress_hooks=[progress_hook],
        postprocessor_hooks=[postprocessor_hook],
        post_hooks=[post_hook_callback],
        platform_key=platform_key,
        cookies_file=cookies_file,
        cookies_from_browser=cookies_from_browser,
    )

    with progress:
        if is_playlist and total_videos and total_videos > 1:
            playlist_task_id = progress.add_task(
                f"[bold bright_magenta]Playlist Progress (0/{total_videos})[/bold bright_magenta]",
                total=total_videos,
            )

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.params["match_filter"] = make_disk_check_filter(
                ydl,
                format_choice=format_choice,
                is_playlist=is_playlist,
                on_skip=on_skip_callback,
            )
            ydl.download([url])

    return {
        "completed": completed_items,
        "skipped": skipped_items,
    }


def view_recent_logs(lines: int = 25):
    """Displays recent log entries from the log file in a clean Rich panel."""
    if not os.path.isfile(LOG_FILE):
        console.print(f"  [dim yellow]No log file found at {LOG_FILE}[/dim yellow]\n")
        return

    try:
        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()

        recent = all_lines[-lines:] if len(all_lines) > lines else all_lines
        log_text = "".join(recent).strip()

        panel = Panel(
            log_text if log_text else "[dim]Log file is currently empty[/dim]",
            title=f"[bold bright_cyan] Recent Logs ({os.path.basename(LOG_FILE)}) [/bold bright_cyan]",
            subtitle=f"[dim]Showing last {len(recent)} entries • Location: {LOG_FILE}[/dim]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
        console.print()
        console.print(panel)
        console.print()
    except Exception as e:
        console.print(f"  [bold red]Could not read log file: {e}[/bold red]\n")


# ====================================================================
#  Interactive Post-Download Action Menu
# ====================================================================

POST_DOWNLOAD_ACTIONS = [
    "Download another video / media / playlist",
    "Open downloads folder in file manager",
    "View recent logs (youtube_downloader.log)",
    "Exit",
]


def generate_post_download_table(selected_index: int) -> Panel:
    """Constructs the styled panel for the interactive post-download action menu."""
    table = Table.grid(padding=(0, 2))
    table.add_column("Key", width=6)
    table.add_column("Option", style="white")

    for idx, opt in enumerate(POST_DOWNLOAD_ACTIONS):
        num = idx + 1
        if idx == selected_index:
            table.add_row(
                f"[bold bright_cyan]> [{num}][/bold bright_cyan]",
                f"[bold bright_white]{opt}[/bold bright_white]",
            )
        else:
            table.add_row(f"  [dim][{num}][/dim]", f"[dim]{opt}[/dim]")

    return Panel(
        table,
        title="[bold bright_cyan] What would you like to do next? [/bold bright_cyan]",
        subtitle="[dim]Use Up/Down arrows or keys 1-4, Enter to confirm[/dim]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )


def interactive_post_download_menu(default_index: int = 0) -> int:
    """
    Renders an interactive post-download action menu with Arrow Key Navigation (↑/↓)
    and direct 1-4 keypresses, Enter to confirm.
    Falls back gracefully to numeric input if not in a TTY.
    """
    num_options = len(POST_DOWNLOAD_ACTIONS)
    selected = default_index

    # Fallback for non-interactive TTY environments
    if not sys.stdin.isatty():
        console.print(generate_post_download_table(selected))
        choice = Prompt.ask(
            "  Choose action",
            choices=[str(i + 1) for i in range(num_options)],
            default=str(default_index + 1),
        )
        return int(choice) - 1

    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    try:
        with Live(generate_post_download_table(selected), console=console, auto_refresh=False) as live:
            while True:
                key = read_key()

                if key in ("UP", "k", "K", "w", "W"):
                    selected = (selected - 1) % num_options
                    live.update(generate_post_download_table(selected), refresh=True)
                elif key in ("DOWN", "j", "J", "s", "S"):
                    selected = (selected + 1) % num_options
                    live.update(generate_post_download_table(selected), refresh=True)
                elif key.isdigit() and 1 <= int(key) <= num_options:
                    selected = int(key) - 1
                    live.update(generate_post_download_table(selected), refresh=True)
                    break
                elif key in ("ENTER", "SPACE"):
                    break
                elif key in ("ESC", "q", "Q"):
                    selected = 3  # Exit
                    break
                elif key == "CTRL_C":
                    raise KeyboardInterrupt
    finally:
        # Restore cursor
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        if sys.platform != "win32":
            try:
                import termios
                termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
            except Exception:
                pass

    chosen = POST_DOWNLOAD_ACTIONS[selected]
    console.print(f"  [bold bright_green]✓ Action:[/bold bright_green] [bold white]{chosen}[/bold white]\n")
    return selected


# ====================================================================
#  Main Application Flow
# ====================================================================

def main():
    app_logger.info("=" * 60)
    app_logger.info(f"Universal Media Downloader Pro started (Python: {sys.version.split()[0]} | OS: {sys.platform})")

    # Clear terminal completely on launcher startup
    os.system("cls" if sys.platform == "win32" else "clear")
    console.clear()

    while True:
        os.system("cls" if sys.platform == "win32" else "clear")
        console.clear()
        render_header()

        # Step 1: Input URL with Next-Level Card and Command Handlers
        render_input_prompt_card()
        url = console.input("  [bold bright_cyan]❯[/bold bright_cyan] [bold cyan]URL[/bold cyan] : ").strip()

        if not url:
            continue

        url_cmd = url.lower()
        if url_cmd in ("q", "quit", "exit"):
            app_logger.info("User requested application exit.")
            render_goodbye_card()
            break
        elif url_cmd in ("cookies", "cookie", "auth"):
            show_cookies_modal()
            Prompt.ask("  Press Enter to return to main menu...")
            continue
        elif url_cmd in ("logs", "log"):
            view_recent_logs()
            Prompt.ask("  Press Enter to return to main menu...")
            continue
        elif url_cmd in ("help", "?"):
            show_help_modal()
            Prompt.ask("  Press Enter to return to main menu...")
            continue
        elif url_cmd in ("clear", "cls"):
            continue

        # Protocol prefix auto-fix
        if not (url.startswith("http://") or url.startswith("https://")):
            if "." in url and not url.startswith("http"):
                url = "https://" + url
            else:
                app_logger.warning(f"Invalid URL entered: {url}")
                console.print("\n  [bold red][ERROR][/bold red] Invalid URL entered. Please provide a valid media link.\n")
                Prompt.ask("  Press Enter to try again...")
                continue

        platform = detect_platform(url)
        app_logger.info(f"Processing URL for platform '{platform['name']}': {url}")
        console.print(f"\n  [bold bright_green]✓ Identified Platform:[/bold bright_green] {platform['badge']}\n")

        # Step 2: Fetch and preview media metadata
        info = fetch_media_info(url)
        if not info:
            app_logger.error(f"Failed to fetch media metadata for URL: {url}")
            Prompt.ask("  Press Enter to continue...")
            continue

        is_playlist, media_title = render_media_card(info, url, platform)
        playlist_count = None

        if is_playlist:
            entries = list(info.get("entries") or [])
            playlist_count = len(entries) if entries else info.get("playlist_count")

        app_logger.info(f"Metadata fetched: '{media_title}' | is_playlist={is_playlist} | items={playlist_count}")

        # Step 3: Check if single video inside a playlist (YouTube)
        playlist_id = extract_playlist_id(url)
        if playlist_id and ("v=" in url or "youtu.be/" in url):
            is_playlist = select_playlist_mode(info, url)
            app_logger.info(f"User mode selection for video inside playlist: is_playlist={is_playlist}")

        # Step 4: Interactive Format & Quality Menu
        profiles = get_format_profiles(platform["key"])
        selected_format = interactive_format_menu(profiles=profiles, default_index=0, platform_name=platform["name"])
        format_profile = profiles[selected_format]
        app_logger.info(f"Format profile chosen: [{selected_format}] {format_profile['name']} ({format_profile['badge']})")

        # Step 5: Destination Folder (Auto-organize by platform)
        default_folder = os.path.join("downloads", platform["folder"])
        console.print(f"  [bold bright_cyan]Destination folder[/bold bright_cyan] [dim](Press Enter for '{default_folder}')[/dim]:")
        folder_input = console.input("  [bold cyan]> [/bold cyan]").strip()
        folder = folder_input if folder_input else default_folder
        full_dest_path = os.path.abspath(folder)
        os.makedirs(full_dest_path, exist_ok=True)
        app_logger.info(f"Destination folder path set to: {full_dest_path}")
        console.print(f"  [bold bright_green]✓ Storage Path:[/bold bright_green] [cyan]{full_dest_path}[/cyan]\n")

        # Step 6: Pre-flight Summary Card
        render_preflight_card(
            title=media_title,
            format_name=f"{format_profile['name']} ({format_profile['badge']})",
            destination_path=full_dest_path,
            is_playlist=is_playlist,
            playlist_count=playlist_count,
            platform=platform,
        )

        # Step 7: Execute Download
        start_time = time.time()
        app_logger.info(f"Starting download execution for: '{media_title}' ({platform['name']})")
        try:
            cookies_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
            active_cookies = cookies_file if os.path.isfile(cookies_file) else None

            download_result = run_download(
                url=url,
                save_path=folder,
                format_choice=selected_format,
                is_playlist=is_playlist,
                total_videos=playlist_count,
                platform_key=platform["key"],
                cookies_file=active_cookies,
            )
            elapsed_sec = int(time.time() - start_time)
            elapsed_str = format_duration(elapsed_sec)

            completed_list = download_result.get("completed", [])
            skipped_list = download_result.get("skipped", [])
            app_logger.info(
                f"Download completed in {elapsed_str}. Completed: {len(completed_list)}, Skipped: {len(skipped_list)}"
            )

            # Step 8: Success Dashboard
            render_success_card(
                title=media_title,
                destination_path=full_dest_path,
                elapsed_str=elapsed_str,
                is_playlist=is_playlist,
                completed_items=completed_list,
                skipped_items=skipped_list,
                platform=platform,
            )

        except KeyboardInterrupt:
            app_logger.warning("Download interrupted by user (KeyboardInterrupt / SIGINT).")
            console.print("\n\n  [bold yellow][ABORT][/bold yellow] Download interrupted by user. Partial downloads saved for auto-resume.\n")
        except Exception as e:
            app_logger.error(f"Error during download execution: {e}", exc_info=True)
            console.print(f"\n\n  [bold red][ERROR][/bold red] An error occurred during download: [dim]{e}[/dim]\n")

        # Step 9: Post-Download Action Menu (Interactive Arrow Key Navigation)
        console.print(Rule(style="dim cyan"))
        action_idx = 0

        while True:
            action_idx = interactive_post_download_menu(default_index=action_idx)
            if action_idx == 0:
                # Download another video / playlist
                break
            elif action_idx == 1:
                # Open downloads folder in file manager
                open_folder(full_dest_path)
            elif action_idx == 2:
                # View recent logs
                view_recent_logs()
            elif action_idx == 3:
                # Exit
                break

        if action_idx == 3:
            app_logger.info("Application closed by user from menu.")
            console.print("\n  [dim]Thank you for using Universal Media Downloader Pro![/dim]\n")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        app_logger.warning("Application terminated via KeyboardInterrupt.")
        console.print("\n  [dim]Application terminated.[/dim]\n")
        sys.exit(0)