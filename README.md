# Universal Media Downloader Pro

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![yt-dlp](https://img.shields.io/badge/Engine-yt--dlp-red?style=for-the-badge)](https://github.com/yt-dlp/yt-dlp)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Lossless%20Merge-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)
[![Rich](https://img.shields.io/badge/UI-Rich%20TUI-brightgreen?style=for-the-badge)](https://github.com/Textualize/rich)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-blue?style=for-the-badge)](https://github.com/)

A state-of-the-art, high-performance command-line media downloader featuring an ultra-modern Terminal User Interface (TUI), automatic static FFmpeg installation (no root/sudo needed), multi-platform URL auto-detection, clipboard sniffing, smart disk deduplication, multi-fragment accelerated streaming, and lossless audio/video merging.

---

## 🌟 Key Features

### 🌐 Multi-Platform Auto-Detection
Paste any URL and the engine automatically identifies the platform and applies tailored format profiles and branding badges:
- **YouTube**: Videos, Shorts, Channels, and full Playlists up to 8K, 4K, 1440p, 1080p60.
- **Facebook**: Public/Private Videos, Reels, and Watch streams in HD & SD.
- **Instagram**: Reels, Posts, and IGTV.
- **TikTok**: High-definition video streams without watermarks.
- **Twitter / X**: Video clips and GIF loops.
- **1,800+ Web Media Sites**: Seamlessly supported via the underlying yt-dlp core.

### ⚡ Aggressive Bandwidth & Acceleration
- **Multi-Threaded Fragment Flooding**: Downloads up to 8 concurrent chunks per stream simultaneously (`CONCURRENT_FRAGMENTS = 8`).
- **Optimized Socket Buffer**: 64 KB socket buffer for maximized packet throughput and zero bandwidth throttling.
- **JavaScript Engine Auto-Integration**: Auto-detects Node.js, Deno, Bun, or QuickJS on your system to execute YouTube JavaScript signature solvers without throttling.

### 🎛️ Dynamic Format & Quality Profiles
- **YouTube Profiles**:
  - `8K / 4K / 1080p60`: Maximum quality video stream merged losslessly with high-bitrate audio via FFmpeg.
  - `1080p Crisp`: Full HD 1080p MP4 optimized for compatibility across all players and devices.
  - `720p Fast`: Compact MP4 file size for quick downloads and mobile playback.
  - `320 kbps MP3`: Studio-grade high-fidelity MP3 extraction.
  - `Best M4A / AAC`: Untouched original source audio container.
- **Social Media Profiles (Facebook / Instagram / TikTok / Twitter)**:
  - `Best Available (HD)`: Highest resolution MP4 available.
  - `HD Crisp (1080p / 720p)`: Balanced high-definition MP4.
  - `SD Compact (480p)`: Lightweight definition for quick sharing.
  - `320 kbps MP3` & `Source M4A`: High-quality audio extraction.

### 🧠 Smart Facebook Title Fallback & Filename Sanitizer
- Facebook videos often lack formal title tags (e.g. `Facebook video #1029384756`). The engine intelligently falls back to the author name and post caption line to construct clean, meaningful filenames.
- Sanitizes illegal filesystem characters across Windows (`\/:*?"<>|`), Linux, and macOS, while enforcing a safe 100-byte length boundary to prevent OS path truncation.

### 💾 Smart Disk Pre-Check & Auto-Resume
- Before initiating any network stream, the disk filter inspects the destination directory. Existing completed files (>1 KB) are skipped immediately.
- Incomplete downloads (`.part` or `.ytdl`) are detected and resumed automatically from the exact byte where they stopped.

### 📋 Clipboard Auto-Detection
- Upon opening the application or returning to the prompt, the app scans the system clipboard:
  - **Linux**: Wayland (`wl-paste`), X11 (`xclip`, `xsel`).
  - **macOS**: `pbpaste`.
  - **Windows & Cross-Platform**: `pyperclip` / Tkinter native hooks.
- If a valid media URL is detected, simply press **Enter** to start processing it immediately without pasting manually.

### 📑 Playlists & Dual-Tracking Progress
- **Intelligent Recognition**: Automatically differentiates between individual videos and playlist URLs.
- **Range Support**: Download full playlists, specific ranges (e.g. `1-10`), or specific indices (e.g. `1,3,7`).
- **Serial File Ordering**: Files are organized with clean two-digit index prefixes: `01. Title.mp4`, `02. Title.mp4`, etc.
- **M3U Playlist Generation**: When downloading audio playlists (MP3 / M4A), an `.m3u` playlist index file is automatically written to the folder for immediate music player playback.
- **Dual Live Bars**: Displays an overall playlist progress bar alongside the active video stream download bar.

### 🔔 Native Desktop Notifications
- Automatically sends native OS desktop alerts upon download completion or errors:
  - **Linux**: Native `notify-send`.
  - **macOS**: AppleScript `osascript` notifications.
  - **Windows**: PowerShell toast / balloon notifications.

### 📁 Custom Download Directory (`path.config`)
- Automatically sorts files into platform subfolders: `downloads/YouTube/`, `downloads/Facebook/`, etc.
- Easily override the default base path by creating or editing `path.config`.

### 🍪 Private / Restricted Content Authentication
- Place an exported `cookies.txt` file in the project directory to effortlessly download private Facebook groups, friends-only posts, follower-restricted Instagram reels, or age-restricted YouTube videos.

### 🛠️ Automatic Static FFmpeg Downloader
- `setup_ffmpeg.py` automatically detects missing FFmpeg binaries and fetches standalone static builds directly from official mirrors (yt-dlp builds / John Van Sickle builds / Gyan.dev) for Linux (x86_64 / arm64) and Windows without requiring administrator/root privileges.

---

## 📂 Project Architecture

```
cross-platform-video-downloader-cli/
│
├── main.py                 # Application bootstrap & Windows UTF-8 / ANSI initialization
├── app.py                  # Core application controller and main event loop
├── setup_ffmpeg.py         # Standalone static FFmpeg downloader and PATH configurator
├── run.sh                  # Automated zero-config launcher for Linux & macOS
├── run.bat                 # Automated zero-config launcher for Windows (UTF-8 enabled)
├── requirements.txt        # Python package dependencies (yt-dlp, rich)
├── path.config             # Custom download directory configuration
├── cookies.txt             # (Optional) Exported cookies for private media authentication
├── youtube_downloader.log  # Rotating diagnostic application logs
│
├── core/
│   ├── config.py           # Constants, bitrate sizing factors, and profile presets
│   ├── detector.py         # Multi-platform domain matching and badge resolution
│   ├── models.py           # Dataclasses (MediaInfo, Platform, FormatOption, DownloadResult)
│   ├── sanitizer.py        # Filename sanitization, time formatting, and Facebook caption parser
│   └── logger.py           # Rotating file logger and rich terminal log viewer
│
├── downloader/
│   ├── engine.py           # High-level downloader orchestrator and Rich progress hooks
│   ├── options.py          # yt-dlp parameter builder and JS engine challenge finder
│   └── disk.py             # SmartDiskChecker for file deduplication and resume handling
│
├── ui/
│   ├── theme.py            # TrueColor pastel palette and title gradient styles
│   ├── banner.py           # Hero banner, platform ribbons, and input prompt
│   ├── cards.py            # Media metadata, preflight summary, and completion cards
│   ├── menus.py            # Interactive format picker and post-download action menus
│   └── modals.py           # Help modal, cookies setup guide, and goodbye screen
│
└── utils/
    ├── clipboard.py        # Cross-platform safe clipboard inspector (Wayland/X11/macOS/Win)
    ├── notify.py           # Native desktop notification dispatcher
    ├── system.py           # Folder opener, media player launcher, and FFmpeg check
    └── terminal.py         # Terminal screen clearer, cursor manager, and raw key reader
```

---

## 🚀 Quick Start & Installation

### 🐧 Linux (Ubuntu, Debian, Linux Mint, Arch, Fedora)

1. Clone or navigate to the project directory:
   ```bash
   cd /path/to/cross-platform-video-downloader-cli
   ```

2. Make `run.sh` executable:
   ```bash
   chmod +x run.sh
   ```

3. Launch the application:
   ```bash
   ./run.sh
   ```

> [!NOTE]
> The automated `./run.sh` launcher handles everything for you:
> - Validates Python 3.
> - Creates and activates a virtual environment (`venv`).
> - Installs and updates `yt-dlp` and `rich`.
> - Checks for FFmpeg, downloading a standalone static binary if missing (no root/sudo password required).
> - Clears the terminal and boots the user interface.

---

### 🪟 Windows (10 / 11)

1. Navigate to the project folder.
2. Double-click `run.bat` or run it from Command Prompt / PowerShell:
   ```cmd
   run.bat
   ```

> [!TIP]
> `run.bat` automatically configures Windows console code page to UTF-8 (`chcp 65001`) and enables Virtual Terminal Processing to render colors, badges, and progress bars smoothly.

---

### 🍎 macOS (Apple Silicon M-series & Intel)

1. Open Terminal and navigate to the project folder:
   ```bash
   cd /path/to/cross-platform-video-downloader-cli
   ```

2. Run the launcher:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

> [!NOTE]
> If FFmpeg is missing, `run.sh` will install it via Homebrew (`brew install ffmpeg`) or configure a static release automatically.

---

### 🐍 Manual Python Execution (Any OS)

If you prefer to manage your environment manually:

```bash
# 1. Create a virtual environment
python3 -m venv venv

# 2. Activate the virtual environment
# Linux / macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
```

---

## ⌨️ Interactive Navigation & In-App Commands

### Main Input Commands
When prompted for a media URL, you can enter any of the following special commands:

| Command | Shortcut | Description |
| :--- | :---: | :--- |
| `q` | `quit`, `exit` | Safely close the application. |
| `path` | `folder`, `dir` | Display the currently configured base download folder. |
| `cookies` | `cookie`, `auth` | Open the Cookie Authentication Guide & check `cookies.txt` status. |
| `logs` | `log` | Inspect the latest entries from `youtube_downloader.log` in terminal. |
| `help` | `?` | Open the help modal and keyboard shortcut cheat sheet. |
| `clear` | `cls` | Clear the screen and refresh the hero dashboard. |

### Quality Selection Controls
Once metadata is loaded, select your preferred format using either:
- **Arrow Keys**: Press `↑` (Up) or `↓` (Down) to browse options, then press `Enter` or `Space` to confirm.
- **Vim Keys**: Press `k` (Up) or `j` (Down).
- **WASD Keys**: Press `w` (Up) or `s` (Down).
- **Direct Numbers**: Press `1`, `2`, `3`, `4`, or `5` to immediately choose the corresponding format.

### Post-Download Action Menu
After a download finishes, choose from interactive actions:
1. `Download another media / playlist` — Return to main prompt.
2. `Open download folder in file manager` — Launches `xdg-open` (Linux), `File Explorer` (Windows), or `open` (macOS).
3. `Play downloaded media in default player` — Opens the downloaded video/audio in VLC, MPV, or default OS player.
4. `View recent download logs` — Check yt-dlp diagnostic outputs.
5. `Exit` — Clean exit.

---

## ⚙️ Configuration

### Custom Destination Path (`path.config`)
By default, media is saved into the project's `downloads/` directory. You can set a custom destination (such as your system Videos folder or an external drive) by editing `path.config` in the root folder:

```ini
# Specify absolute or relative path:
PATH="/home/sumon/Videos"
```
Or simply:
```text
/home/sumon/Videos
```
Windows example:
```ini
PATH="D:\Media\Downloads"
```

The application automatically creates organized platform subfolders within your target path:
```
/home/sumon/Videos/
├── YouTube/
├── Facebook/
├── Instagram/
├── TikTok/
├── Twitter/
└── WebMedia/
```

---

### Cookie Authentication (`cookies.txt`)
Some videos require user authentication (e.g., Facebook private group videos, Instagram follower-only reels, or age-restricted YouTube videos).

#### How to Set Up Cookies in 2 Minutes:
1. Install a browser extension such as **"Get cookies.txt LOCALLY"** (available for Chrome, Brave, Firefox, Edge).
2. Visit the website (e.g. `facebook.com` or `youtube.com`) while logged into your account.
3. Click the extension icon and export your cookies as Netscape format.
4. Save the file as **`cookies.txt`** directly in the root directory of this project:
   ```
   cross-platform-video-downloader-cli/cookies.txt
   ```
5. Type `cookies` inside the app anytime to verify that the file is loaded and active.

---

## 🔧 Troubleshooting & FAQ

### 1. `[ERROR] Required packages are missing!`
Run `./run.sh` (Linux/macOS) or `run.bat` (Windows). The launchers automatically create a virtual environment and run `pip install -r requirements.txt`.

### 2. FFmpeg not found or stream merging disabled
- If running manually without `run.sh`/`run.bat`, execute:
  ```bash
  python setup_ffmpeg.py
  ```
- Alternatively, install FFmpeg system-wide:
  - **Ubuntu / Debian**: `sudo apt install ffmpeg`
  - **Arch Linux**: `sudo pacman -S ffmpeg`
  - **macOS**: `brew install ffmpeg`
  - **Windows**: `winget install Gyan.FFmpeg` or download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).

### 3. "Sign in to confirm you're not a bot" or "Private Video"
- Export your browser cookies using the Netscape format and place `cookies.txt` in the root directory.
- Ensure you have Node.js or Bun installed; the downloader will automatically detect it to solve YouTube player JavaScript challenges.

### 4. How to cancel an in-progress download?
Press `Ctrl + C` at any time. The application cleanly aborts the download, restores your terminal cursor, and preserves any `.part` files so they can be resumed later.

---

## 📜 Dependencies & Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — The engine powering high-speed video/audio extraction.
- [Rich](https://github.com/Textualize/rich) — Terminal rendering engine for tables, live progress bars, and modal panels.
- [FFmpeg](https://ffmpeg.org/) — Industry-standard multimedia framework for lossless stream merging and audio transcoding.

