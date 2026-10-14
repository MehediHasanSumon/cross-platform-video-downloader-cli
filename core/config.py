"""Application configuration, constants, and quality profiles."""

import os
import sys

# Brand & System Metadata
APP_NAME = "VIDEO DOWNLOADER"
VERSION = "3.6"
AUTHOR = "Md Mehedi Hasan"

# Base filesystem directories
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DOWNLOAD_DIR = os.path.join(ROOT_DIR, "downloads")
LOG_FILE = os.path.join(ROOT_DIR, "youtube_downloader.log")
COOKIES_FILE = os.path.join(ROOT_DIR, "cookies.txt")

# Supported Platform Ribbon Configuration
SUPPORTED_PLATFORMS = [
    {"name": "YouTube", "badge_color": "#f87070", "fg": "#121316"},
    {"name": "Facebook", "badge_color": "#60a4fa", "fg": "#121316"},
    {"name": "Instagram", "badge_color": "#e778f9", "fg": "#121316"},
    {"name": "TikTok", "badge_color": "#27d2ed", "fg": "#121316"},
    {"name": "Twitter/X", "badge_color": "#f3f4f6", "fg": "#121316"},
]

# Format & Quality Profiles with typical bitrate / size factors for estimation
YOUTUBE_FORMAT_PROFILES = [
    {
        "id": 0,
        "name": "Maximum Quality Video",
        "badge": "8K / 4K / 1080p60",
        "desc": "Lossless Video + Best Audio merged via FFmpeg (MP4)",
        "ext": "mp4",
        "tag": "ULTRA HD",
        "tag_color": "bright_cyan",
        "est_mb_per_min": 45.0,
        "codec": "H.264 / AV1 + AAC",
    },
    {
        "id": 1,
        "name": "1080p Full HD Video",
        "badge": "1080p Crisp",
        "desc": "Standard 1080p High-Definition MP4 (Optimal Compatibility)",
        "ext": "mp4",
        "tag": "FULL HD",
        "tag_color": "bright_green",
        "est_mb_per_min": 22.0,
        "codec": "H.264 + AAC",
    },
    {
        "id": 2,
        "name": "720p HD Video",
        "badge": "720p Fast",
        "desc": "Fast download, compact file size, great for mobile (MP4)",
        "ext": "mp4",
        "tag": "COMPACT",
        "tag_color": "yellow",
        "est_mb_per_min": 11.0,
        "codec": "H.264 + AAC",
    },
    {
        "id": 3,
        "name": "High-Fidelity Audio (MP3)",
        "badge": "320 kbps MP3",
        "desc": "Ultra high-bitrate studio audio extraction",
        "ext": "mp3",
        "tag": "AUDIO MP3",
        "tag_color": "bright_magenta",
        "est_mb_per_min": 2.4,
        "codec": "MP3 320kbps CBR",
    },
    {
        "id": 4,
        "name": "Original Audio (M4A)",
        "badge": "Best M4A / AAC",
        "desc": "Untouched original source audio stream",
        "ext": "m4a",
        "tag": "RAW AUDIO",
        "tag_color": "cyan",
        "est_mb_per_min": 1.4,
        "codec": "AAC Source",
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
        "est_mb_per_min": 25.0,
        "codec": "MP4 / AAC",
    },
    {
        "id": 1,
        "name": "High Definition (1080p / 720p)",
        "badge": "HD Crisp",
        "desc": "High-definition MP4 stream for fast download & crisp playback",
        "ext": "mp4",
        "tag": "HD MP4",
        "tag_color": "bright_green",
        "est_mb_per_min": 15.0,
        "codec": "H.264 + AAC",
    },
    {
        "id": 2,
        "name": "Standard Definition (SD / 480p)",
        "badge": "SD 480p Compact",
        "desc": "Standard definition MP4, lightweight and great for sharing",
        "ext": "mp4",
        "tag": "SD COMPACT",
        "tag_color": "yellow",
        "est_mb_per_min": 7.0,
        "codec": "H.264 + AAC",
    },
    {
        "id": 3,
        "name": "High-Fidelity Audio (MP3)",
        "badge": "320 kbps MP3",
        "desc": "Extract studio-quality 320kbps MP3 audio soundtrack",
        "ext": "mp3",
        "tag": "AUDIO MP3",
        "tag_color": "bright_magenta",
        "est_mb_per_min": 2.4,
        "codec": "MP3 320kbps CBR",
    },
    {
        "id": 4,
        "name": "Original Audio (M4A / AAC)",
        "badge": "Source Audio",
        "desc": "Untouched original audio stream directly from media",
        "ext": "m4a",
        "tag": "RAW AUDIO",
        "tag_color": "cyan",
        "est_mb_per_min": 1.4,
        "codec": "AAC Source",
    },
]

POST_DOWNLOAD_ACTIONS = [
    "Download another media / playlist",
    "Open download folder in file manager",
    "Play downloaded media in default player",
    "View recent download logs",
    "Exit",
]
