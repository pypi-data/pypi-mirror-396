## ⭐️ misato

A tool for downloading videos from the "MissAV" website.

Misato is an upgraded version of Miyuki, capable of bypassing Cloudflare in certain situations.

## 📌 Prerequisites

1. Add the **Chrome.exe** path to the **MISATO_CHROME_EXE** environment variable.

```
set MISATO_CHROME_EXE="C:\Program Files\Google\Chrome\Application\chrome.exe"
```

2. Install FFmpeg (Optional, Recommend)

Please refer to https://ffmpeg.org/

## ⚙️ Installation

To install misato from the Python Package Index (PyPI) run:

```
pip install misato
```

To upgrade misato from the Python Package Index (PyPI) run:

```
pip install --upgrade misato
```

## 📷 Snapshot

![snapshot.png](resources/readme_pics/snapshot.png)

## 📖 Instructions

```
PS C:\Users\Administrator> misato -h
misato - 2025-12-14 15:28:41 - INFO     - misato - Logger initialized | Level: INFO | JSON: False | File: C:\Users\Administrator\PycharmProjects\MissAV-Downloader\logs\misato.log
misato - 2025-12-14 15:28:42 - INFO     - misato - Existing Chrome detected, reusing it
misato - 2025-12-14 15:28:42 - INFO     - misato - Connecting to Chrome via CDP
misato - 2025-12-14 15:28:42 - INFO     - misato - Successfully connected to Chrome
usage: misato [-h] (-auto URL [URL ...] | -search CODE | -file PATH)
              [-limit LIMIT] [-proxy PROXY] [-ffmpeg] [-cover] [-ffcover]
              [-noban] [-title] [-quality QUALITY] [-retry RETRY]
              [-delay DELAY] [-timeout TIMEOUT]

Misato - MissAV video downloader

options:
  -h, --help           show this help message and exit
  -auto URL [URL ...]  One or more video or playlist URLs (can be mixed)
  -search CODE         Search video by code (e.g., roe-414)
  -file PATH           Text file containing URLs (one per line)
  -limit LIMIT         Maximum number of videos to download
  -proxy PROXY         HTTP/HTTPS proxy (host:port)
  -ffmpeg              Enable FFmpeg merging for best quality
  -cover               Download video cover image
  -ffcover             Embed cover as video thumbnail (requires FFmpeg)
  -noban, --no-banner  Suppress the ASCII art banner
  -title               Use full video title as filename
  -quality QUALITY     Preferred resolution (e.g., 720, 1080)
  -retry RETRY         Number of retries per segment
  -delay DELAY         Delay between retries in seconds
  -timeout TIMEOUT     Timeout per segment download in seconds

Examples:
  misato -auto https://missav.ws/roe-414 -ffcover -title -quality 720
  misato -auto https://missav.ws/actresses/JULIA -limit 20 -ffmpeg
  misato -search roe-414 -ffcover
  misato -file urls.txt -title -proxy localhost:7890
```

## 💬 The ```-auto``` option

- Use the -auto option to download movies from a playlist.
- This playlist can be a public playlist created by your own account, or any playlist displayed based on search results or tag filters.
- **You should wrap the playlist URL with " " when you use the -auto option.**

Command Examples:
- ```misato -auto "https://missav.ai/search/JULIA?filters=uncensored-leak&sort=saved" -limit 50 -ffmpeg```
- ```misato -auto "https://missav.ai/search/JULIA?filters=individual&sort=views" -limit 20 -ffmpeg```
- ```misato -auto "https://missav.ai/dm132/actresses/JULIA" -limit 20 -ffmpeg```
- ```misato -auto "https://missav.ai/playlists/ewzoukev" -limit 20 -ffmpeg```
- ```misato -auto "https://missav.ai/dm444/en/labels/WANZ" -limit 20 -ffmpeg```
- ```misato -auto "https://missav.ai/dm21/en/makers/Takara%20Visual" -limit 20 -ffmpeg```
- ```misato -auto "https://missav.ai/dm1/en/genres/4K" -limit 20 -ffmpeg```

## 💡 Precautions

- If you are from an ancient oriental country, you will most likely need a proxy.
- Use ffmpeg to synthesize videos for the best experience.

## 👀 About FFmpeg

1. If you want misato to use ffmpeg to process the video, use the -ffmpeg option.
2. Please check whether the ffmpeg command is valid before using the -ffmpeg option. (e.g. ```ffmpeg -version```)

## 📄 Disclaimer

This project is licensed under the [MIT License](LICENSE). The following additional disclaimers and notices apply:

### 1. Legal Compliance
- This software is provided solely for **communication, research, learning, and personal use**.  
- Users are responsible for ensuring that their use of this software complies with all applicable laws and regulations in their jurisdiction.  
- The software must not be used for any unlawful, unethical, or unauthorized purposes, including but not limited to violating third-party rights or legal restrictions.

### 2. No Warranty
As stated in the MIT License:  
> "THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT."

### 3. Limitation of Liability
- The author(s) shall not be held liable for any claims, damages, or other liabilities arising from or in connection with the use or performance of this software.  
- Users bear all risks and responsibilities for the use of this software, including but not limited to data loss, system damage, or legal consequences.

### 4. Third-Party Dependencies
- This project may include or depend on third-party libraries or tools. Users are responsible for reviewing and complying with the licenses and terms of these dependencies.

### 5. Security and Privacy
- This software may interact with user systems, networks, or data. Users should implement appropriate security measures to protect sensitive information and infrastructure.  
- The authors are not responsible for any security vulnerabilities or data breaches resulting from the use of this software.
