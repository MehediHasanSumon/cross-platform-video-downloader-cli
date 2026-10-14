"""Title cleaning, time formatting, and parameter parsing."""

import urllib.parse
from typing import Optional, Dict, Any

class Sanitizer:
    """Provides methods for string, duration, size, and title sanitization."""

    @staticmethod
    def format_duration(seconds: Any) -> str:
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

    @staticmethod
    def format_views(views: Any) -> str:
        if views is None:
            return "N/A"
        try:
            val = int(round(float(views)))
            return f"{val:,} views"
        except (ValueError, TypeError):
            views_str = str(views).strip()
            return "N/A" if not views_str else f"{views_str} views"

    @staticmethod
    def format_file_size(bytes_val: Any) -> str:
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

    @staticmethod
    def extract_playlist_id(url: str) -> Optional[str]:
        try:
            parsed = urllib.parse.urlparse(url)
            qs = urllib.parse.parse_qs(parsed.query)
            if "list" in qs and qs["list"]:
                return qs["list"][0]
        except Exception:
            pass
        return None

    @staticmethod
    def clean_media_title(info: Dict[str, Any], platform_key: str) -> str:
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

        # Enforce cross-platform safe filename length
        if len(cleaned.encode("utf-8", errors="ignore")) > 180:
            cleaned = cleaned[:60] + "..."

        return cleaned or "Media_Download"
