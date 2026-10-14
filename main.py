#!/usr/bin/env python3
"""
====================================================================
 Universal Media Downloader Pro
 Next-Level Multi-Platform Terminal User Interface (TUI)
 Powered by yt-dlp, FFmpeg, and Rich
 Developed by Md Mehedi Hasan
====================================================================
"""

import sys
import ctypes

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
            kernel32.SetConsoleMode(h_stdout, mode.value | 0x0004)
    except Exception:
        pass

# Verify essential dependencies
try:
    import yt_dlp
    import rich
except ImportError:
    print("\n\033[91m[ERROR] Required packages are missing!\033[0m")
    launcher = "run.bat" if sys.platform == "win32" else "./run.sh"
    print(f"Please run '{launcher}' or install: pip install -r requirements.txt\n")
    sys.exit(1)

from app import MediaDownloaderApp

def main():
    app = MediaDownloaderApp()
    return app.run()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\033[93mApplication terminated by user.\033[0m\n")
        sys.exit(0)