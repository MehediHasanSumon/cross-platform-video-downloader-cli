"""Factory for yt-dlp parameter dictionaries."""

import os
from typing import Optional, List, Dict, Any
from core.logger import AppLogger, YtDlpLogger

class YdlOptionsBuilder:
    """Constructs tailored yt-dlp configuration dictionaries."""

    @staticmethod
    def build(
        save_path: str,
        format_choice: int,
        is_playlist: bool,
        progress_hooks: List[Any],
        postprocessor_hooks: List[Any],
        post_hooks: List[Any],
        platform_key: str = "generic",
        cookies_file: Optional[str] = None,
        cookies_from_browser: Optional[str] = None,
        playlist_title: Optional[str] = None,
        playlist_items: Optional[str] = None,
    ) -> Dict[str, Any]:
        os.makedirs(save_path, exist_ok=True)

        if is_playlist:
            # 1. Folder named after the playlist (using extracted playlist_title or metadata fallback)
            clean_fallback = playlist_title.strip() if playlist_title else "Playlist"
            folder_part = f"%(playlist_title,playlist|{clean_fallback})s"
            # 2. Numbered serial prefix: 01. , 02. , 03. etc.
            file_part = "%(playlist_index,playlist_autonumber&{:02d}. |)s%(title,id)s.%(ext)s"
            out_template = os.path.join(save_path, folder_part, file_part)
        else:
            out_template = os.path.join(save_path, "%(title,id)s.%(ext)s")

        ydl_opts: Dict[str, Any] = {
            "outtmpl": {"default": out_template},
            "windowsfilenames": True,
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
            "logger": YtDlpLogger(AppLogger.get_logger()),
            "noprogress": True,
            "quiet": True,
            "no_warnings": True,
        }

        if is_playlist and playlist_items:
            ydl_opts["playlist_items"] = str(playlist_items).strip()

        if cookies_file and os.path.isfile(cookies_file):
            ydl_opts["cookiefile"] = cookies_file
        elif cookies_from_browser:
            ydl_opts["cookiesfrombrowser"] = (cookies_from_browser, None, None, None)

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
