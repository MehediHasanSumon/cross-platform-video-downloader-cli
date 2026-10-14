"""Safe clipboard detection across Linux, Windows, and macOS."""

import sys
import shutil
import subprocess
from typing import Optional

class ClipboardHelper:
    """Reads system clipboard safely across environments."""

    @staticmethod
    def get_clipboard_text() -> Optional[str]:
        # 1. Try Wayland wl-paste on Linux
        if sys.platform != "win32" and shutil.which("wl-paste"):
            try:
                res = subprocess.run(
                    ["wl-paste", "--no-newline"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    timeout=0.2,
                )
                if res.returncode == 0 and res.stdout:
                    return res.stdout.strip()
            except Exception:
                pass

        # 2. Try Tkinter (Standard library, works on Windows/macOS/Linux)
        try:
            import tkinter
            root = tkinter.Tk()
            root.withdraw()
            text = root.clipboard_get()
            root.destroy()
            if text:
                return text.strip()
        except Exception:
            pass

        # 3. Try xclip on Linux (X11)
        if sys.platform != "win32" and shutil.which("xclip"):
            try:
                res = subprocess.run(
                    ["xclip", "-selection", "clipboard", "-o"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    timeout=0.2,
                )
                if res.returncode == 0 and res.stdout:
                    return res.stdout.strip()
            except Exception:
                pass

        # 4. Try pyperclip if installed
        try:
            import pyperclip
            val = pyperclip.paste()
            if val:
                return val.strip()
        except Exception:
            pass

        return None

    @classmethod
    def get_media_url_candidate(cls) -> Optional[str]:
        """Returns clipboard text if it looks like a media link."""
        text = cls.get_clipboard_text()
        if not text:
            return None
        text_lower = text.lower()
        if any(term in text_lower for term in ["youtube.com", "youtu.be", "facebook.com", "fb.watch", "instagram.com", "tiktok.com", "twitter.com", "x.com"]):
            if text.startswith("http://") or text.startswith("https://"):
                return text
            return f"https://{text}"
        return None
