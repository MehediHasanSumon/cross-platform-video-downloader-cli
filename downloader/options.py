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
    ) -> Dict[str, Any]:
        os.makedirs(save_path, exist_ok=True)

        if is_playlist:
            out_template = os.path.join(
                save_path,
                "%(playlist_title|Playlist)s",
                "%(playlist_index&{:02d} - |)s%(title,id)s.%(ext)s",
            )
        else:
            out_template = os.path.join(save_path, "%(title,id)s.%(ext)s")

        ydl_opts: Dict[str, Any] = {
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
            "logger": YtDlpLogger(AppLogger.get_logger()),
            "noprogress": True,
            "quiet": True,
            "no_warnings": True,
        }

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
