# Universal Media Downloader Pro (YouTube, Facebook & Social TUI)

A state-of-the-art, interactive command-line media and video downloader with automated dependency setup, multi-platform auto-detection, real-time metadata preview, lossless FFmpeg merging, and an ultra-modern Terminal User Interface (TUI).

Supports:
- **YouTube** (Videos, Shorts, Playlists up to 8K, 4K, 1440p, 1080p60)
- **Facebook** (Reels, Watch, Page Videos, HD & SD downloads)
- **Instagram** (Reels, Videos)
- **TikTok**, **Twitter / X**, and **1,800+ other web media sites**
- **Studio-Quality Audio Extraction** (320kbps MP3 & Original M4A/AAC)

Works seamlessly on **Linux (Ubuntu / Debian / Mint / Arch / Fedora)**, **Windows (10 / 11)**, and **macOS (Apple Silicon & Intel)**.

---

## 🚀 How to Run

### 🐧 Linux (Ubuntu / Debian / Mint)

1. Open your terminal in this project folder:
   ```bash
   cd /path/to/youtube-downloader
   ```

2. Make `run.sh` executable (if not already):
   ```bash
   chmod +x run.sh
   ```

3. Launch the downloader:
   ```bash
   ./run.sh
   ```

> [!NOTE]
> The launcher (`./run.sh`) automatically:
> - Verifies Python 3 is installed.
> - Creates and activates a virtual environment (`venv`).
> - Installs `yt-dlp` and `rich` from `requirements.txt`.
> - Checks for FFmpeg (and automatically downloads a standalone static Linux build if missing — **no root/sudo password required!**).
> - Launches `main.py`.

---

### 🪟 Windows

1. Double-click `run.bat` or run in CMD / PowerShell:
   ```cmd
   run.bat
   ```

---

### 🍎 macOS (Apple Silicon & Intel)

1. Open Terminal in the project folder:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
> [!TIP]
> Compatible with both Apple Silicon (M1/M2/M3/M4) and Intel Macs. FFmpeg will be configured automatically or you can install it via `brew install ffmpeg`.

---

## 💎 Next-Level UI/UX Features

- **🌐 Multi-Platform Auto-Detection**: Paste any link (YouTube, Facebook, Instagram, TikTok, Twitter/X) — the engine instantly detects the platform and displays dynamic branding badges.
- **⚡ Adaptive Format Profiles**: Tailored format choices based on detected platform:
  - *YouTube*: 8K / 4K / 1440p / 1080p60 / 720p / MP3 / M4A.
  - *Facebook & Social*: Best Available HD / 1080p / SD 480p / MP3 320kbps / M4A.
- **🏷️ Smart Facebook Title & Filename Fallback**: Resolves generic titles (`Facebook video #123456`) into readable file names using post captions and creator names.
- **📁 Smart Platform Organization**: Automatically sorts media into `downloads/Facebook/`, `downloads/YouTube/`, `downloads/Instagram/`, etc. (or use your custom folder).
- **🍪 Private / Restricted Media Support (Cookies)**: Place your `cookies.txt` in the project root to download private group videos, friend-only posts, or restricted reels.
- **Visual Hero Header & Status Badges**: Clean, branded dashboard displaying engine, FFmpeg, cookies, and OS status.
- **Instant Media Information Card**: Fetches video metadata with a live spinner and displays title, channel/artist, duration, view count, and content type before downloading.
- **Interactive Keyboard Navigation**: Smoothly navigate format options using keyboard arrow keys (`↑` / `↓`) and `Enter`, or press number keys (`1`–`5`) directly.
- **Maximum Quality**: Downloads the best video stream and best audio stream, then losslessly merges them into MP4 via FFmpeg.
- **Smart Disk Check & Auto-Resume**: Checks your destination folder directly before downloading. Files already on disk are skipped automatically. Incomplete downloads (`.part`) automatically resume from where they stopped.
- **Live Real-Time Rich Progress Engine**: Real-time progress bar tracking stream download, percentage, MB downloaded / total, speed in MB/s, and ETA. Separate status indicators for video download, audio download, and FFmpeg stream merging.
- **Playlist Dual-Tracking**: Shows overall playlist progress alongside the active video's download progress.
- **Completed Items Dashboard**: Displays real-time `✓ Completed` notifications for each video along with a structured summary table showing download status and file size.
- **Dedicated Log File (`youtube_downloader.log`)**: Automatically logs all downloads, skips, errors, and yt-dlp diagnostic messages. You can inspect logs directly from the interactive post-download menu.
- **Post-Download Action Dashboard**: Upon completion, view the download summary with an option to open the downloads folder directly in your system file manager (`xdg-open` on Linux, `File Explorer` on Windows).

---

## 🇧🇩 বাংলা নির্দেশিকা (Quick Guide in Bengali)

### 🐧 লিনাক্স (Ubuntu / Debian / Mint / Arch):
টার্মিনালে প্রজেক্ট ফোল্ডারে গিয়ে রান করুন:
```bash
chmod +x run.sh
./run.sh
```
`run.sh` স্বয়ংক্রিয়ভাবে Python ভার্চুয়াল এনভায়রনমেন্ট তৈরি করবে, `yt-dlp` ও `rich` ইন্সটল করবে এবং FFmpeg না থাকলে স্বয়ংক্রিয়ভাবে ডাউনলোড ও কনফিগার করে নেবে (কোনো root/sudo পাসওয়ার্ড লাগবে না)। চেক শেষ হওয়ার পর টার্মিনাল স্বয়ংক্রিয়ভাবে ক্লিয়ার হয়ে ফ্রেশ ইন্টারফেস ওপেন হবে।

### 🪟 উইন্ডোজ (Windows 10 / 11):
সরাসরি `run.bat` ফাইলে ডাবল ক্লিক করুন অথবা CMD / PowerShell থেকে চালান:
```cmd
run.bat
```
উইন্ডোজে বাংলা লেখা এবং আধুনিক কালার ইন্টারফেস ঠিক রাখার জন্য এতে স্বয়ংক্রিয় UTF-8 (Code Page 65001) মোড এনাবল করা আছে।

### 🍎 ম্যাক (macOS Apple Silicon & Intel):
ম্যাক টার্মিনালে রান করুন:
```bash
chmod +x run.sh
./run.sh
```
M1/M2/M3/M4 বা Intel যে কোনো ম্যাকের জন্যই এটি স্বয়ংক্রিয়ভাবে পরিবেশ প্রস্তুত করে নেবে।

### নতুন নেক্সট-লেভেল ফিচারসমূহ:
1. **ফেসবুক ও মাল্টি-প্ল্যাটফর্ম সাপোর্ট**: Facebook (Reels, Watch, Video), YouTube, Instagram, TikTok যেকোনো লিঙ্ক দিলেই স্বয়ংক্রিয়ভাবে ডিটেক্ট করে ডাউনলোড করা যাবে।
2. **স্মার্ট ফেসবুক টাইটেল**: ফেসবুক ভিডিওর টাইটেল মিসিং বা কেবল আইডি নাম্বার হলে, পোস্টের ক্যাপশন ও পেজের নাম ব্যবহার করে সুন্দর ও বোধগম্য ফাইল তৈরি করে।
3. **ডাইনামিক কোয়ালিটি মেনু**: ফেসবুকের জন্য সরাসরি HD ও SD কোয়ালিটি এবং ইউটিউবের জন্য 8K/4K/1080p অপশন ডাইনামিকভাবে আসবে। অ্যারো কি (`↑`/`↓`) দিয়ে সহজেই সিলেক্ট করা যাবে।
4. **অটো প্ল্যাটফর্ম ফোল্ডার**: ডাউনলোড করা ফাইলগুলো স্বয়ংক্রিয়ভাবে প্ল্যাটফর্ম অনুযায়ী সাজানো থাকবে (`downloads/Facebook/`, `downloads/YouTube/`)।
5. **প্রাইভেট ভিডিও ও কুকিজ সাপোর্ট**: ফেসবুক প্রাইভেট গ্রুপ বা বন্ধুদের পোস্টের ভিডিও ডাউনলোডের জন্য প্রোজেক্ট ফোল্ডারে `cookies.txt` রাখলেই অ্যাপটি স্বয়ংক্রিয়ভাবে তা ব্যবহার করবে।
6. **রিয়েলটাইম প্রগ্রেস ও অটো-রিজিউম**: ডাউনলোড স্পিড, ETA এবং ডিস্কে আগে থেকে ফাইল থাকলে অটো-স্কিপ ও অসম্পূর্ণ থাকলে সেখান থেকেই রিজুউম করার সুবিধা।
