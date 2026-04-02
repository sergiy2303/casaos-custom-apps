# Tuya Camera .media to MP4 Converter

Converts proprietary `.media` files from Tuya/Smart Life wifi camera SD cards to standard `.mp4` files with audio.

## Background

Tuya cameras store recordings on SD cards in a proprietary `.media` format that can only be played back through the Tuya Smart app. This script extracts the H.265 video and G.711 A-law audio streams and remuxes them into a standard MP4 container.

## Dependencies

### Python 3.6+

The script uses only standard library modules (`struct`, `subprocess`, `sys`, `os`, `glob`, `tempfile`, `concurrent.futures`, `multiprocessing`) — no pip packages required.

**Linux (Debian/Ubuntu):**
```bash
sudo apt install python3
```

**macOS:**
```bash
brew install python3
```

**Windows:**

Download from https://www.python.org/downloads/ and install. Make sure to check "Add Python to PATH" during installation.

### FFmpeg

Required for muxing the extracted streams into MP4.

**Linux (Debian/Ubuntu):**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**

Download from https://ffmpeg.org/download.html (use the "gyan.dev" or "BtbN" builds). Extract and add the `bin` folder to your system PATH.

Alternatively, install via package managers:
```powershell
# winget
winget install Gyan.FFmpeg

# chocolatey
choco install ffmpeg

# scoop
scoop install ffmpeg
```

## Usage

### Convert a single file

```bash
python3 tuya_media_to_mp4.py recording.media
```

Output will be saved as `recording.mp4` in the same directory.

### Convert a single file with custom output path

```bash
python3 tuya_media_to_mp4.py recording.media /path/to/output.mp4
```

### Batch convert all files in a directory

```bash
python3 tuya_media_to_mp4.py /path/to/sd_card/
```

This recursively finds all `.media` files and converts each one to `.mp4` in place (next to the original file). Already converted files (where a `.mp4` exists) are skipped automatically, so it's safe to re-run.

### Parallel processing

Batch mode uses multiple worker processes for faster conversion. By default it uses `min(cpu_cores, 8)` workers.

```bash
# Use 16 parallel workers
python3 tuya_media_to_mp4.py /path/to/sd_card/ --workers 16
```

Progress is displayed with a files/second rate and ETA:

```
[42/10000] OK: 2025/07/15/10/0010.media — 155318 bytes, 462 frames  (30.1 files/s, ETA 5m31s)
```

### Reconvert existing files

By default, files that already have a corresponding `.mp4` are skipped. Use `--force` to reconvert them:

```bash
python3 tuya_media_to_mp4.py /path/to/sd_card/ --force
```

### Typical SD card folder structure

Tuya cameras organize recordings on the SD card like this:

```
SD_CARD/
  2025/
    07/
      15/
        10/
          .info
          0000.media
          0010.media
          0020.media
          1752577253.jpg
        11/
          ...
```

To convert an entire SD card:

```bash
python3 tuya_media_to_mp4.py /media/sdcard/
```

### Performance estimates

| Workers | Approx. speed  | 100k files |
|---------|----------------|------------|
| 4       | ~30 files/s    | ~55 min    |
| 8       | ~60 files/s    | ~28 min    |
| 16      | ~100 files/s   | ~17 min    |

Actual speed depends on disk I/O and file sizes. SSD will be significantly faster than SD card.

## .media File Format

| Offset | Size | Type       | Description                              |
|--------|------|------------|------------------------------------------|
| 0      | 4    | uint32_le  | Frame type: 1 = I-frame, 0 = P-frame, 3 = audio |
| 4      | 4    | uint32_le  | Payload size in bytes                    |
| 8      | 4    | uint32_le  | Timestamp                                |
| 12     | 12   | —          | Reserved fields                          |
| 24     | N    | bytes      | Payload (H.265 NAL units or G.711 audio) |

- **Video codec:** H.265/HEVC
- **Audio codec:** G.711 A-law, 8000 Hz, mono
- **Container metadata:** `.info` JSON file with `version`, `eventType`, and `codec` fields

## Troubleshooting

**`ffmpeg: command not found`**
FFmpeg is not installed or not in your PATH. See the Dependencies section above.

**`No video data found, skipping`**
The `.media` file may be corrupted or empty.

**Output has no audio**
Some recordings are silent (the camera mic picks up no sound). The audio track will still be included but will contain silence.

**Windows: `python3` not recognized**
Try `python` instead of `python3` on Windows:
```powershell
python tuya_media_to_mp4.py recording.media
```
