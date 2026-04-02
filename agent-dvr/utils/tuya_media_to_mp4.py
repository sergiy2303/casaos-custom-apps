#!/usr/bin/env python3
"""
Convert Tuya camera .media files to MP4 with audio.

Tuya .media format:
  - Each frame has a 24-byte header:
    [0:4]  uint32_le  frame_type (1=I-frame, 0=P-frame, 3=audio)
    [4:8]  uint32_le  payload_size
    [8:12] uint32_le  timestamp
    [12:24]           reserved fields
  - Video: H.265/HEVC raw NAL units
  - Audio: G.711 A-law, 8kHz, mono, 256 bytes per frame

Usage:
  python3 tuya_media_to_mp4.py <input.media> [output.mp4]
  python3 tuya_media_to_mp4.py /path/to/sd_card_folder/                # batch, default workers
  python3 tuya_media_to_mp4.py /path/to/sd_card_folder/ --workers 16   # batch, 16 workers
"""

import struct
import subprocess
import sys
import os
import glob
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count


def parse_media_file(filepath):
    """Parse a Tuya .media file and extract video/audio streams."""
    with open(filepath, "rb") as f:
        data = f.read()

    video_data = bytearray()
    audio_data = bytearray()
    offset = 0
    frame_count = 0

    while offset < len(data) - 24:
        frame_type = struct.unpack_from("<I", data, offset)[0]
        payload_size = struct.unpack_from("<I", data, offset + 4)[0]

        if payload_size == 0 or offset + 24 + payload_size > len(data):
            break

        payload = data[offset + 24 : offset + 24 + payload_size]

        if frame_type in (0, 1):  # video (I-frame or P-frame)
            video_data.extend(payload)
        elif frame_type == 3:  # audio
            audio_data.extend(payload)

        offset += 24 + payload_size
        frame_count += 1

    return video_data, audio_data, frame_count


def convert_file(input_path, output_path=None):
    """Convert a single .media file to .mp4. Returns (input_path, success, message)."""
    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".mp4"

    try:
        video_data, audio_data, frame_count = parse_media_file(input_path)

        if not video_data:
            return (input_path, False, "No video data found")

        with tempfile.NamedTemporaryFile(suffix=".h265", delete=False) as vf:
            vf.write(video_data)
            video_tmp = vf.name

        audio_tmp = None
        try:
            ffmpeg_cmd = ["ffmpeg", "-y", "-f", "hevc", "-i", video_tmp]

            if audio_data:
                with tempfile.NamedTemporaryFile(suffix=".raw", delete=False) as af:
                    af.write(audio_data)
                    audio_tmp = af.name
                ffmpeg_cmd += ["-f", "alaw", "-ar", "8000", "-ac", "1", "-i", audio_tmp]
                ffmpeg_cmd += ["-c:v", "copy", "-c:a", "aac", output_path]
            else:
                ffmpeg_cmd += ["-c:v", "copy", output_path]

            result = subprocess.run(
                ffmpeg_cmd, capture_output=True, text=True, timeout=120
            )

            if result.returncode != 0:
                return (input_path, False, f"ffmpeg error: {result.stderr[-200:]}")

            size = os.path.getsize(output_path)
            return (input_path, True, f"{size} bytes, {frame_count} frames")

        finally:
            os.unlink(video_tmp)
            if audio_tmp:
                os.unlink(audio_tmp)

    except Exception as e:
        return (input_path, False, str(e))


def batch_convert(media_files, workers):
    """Convert files in parallel using multiple processes."""
    total = len(media_files)
    success = 0
    failed = 0
    start_time = time.time()

    print(f"Converting {total} files with {workers} workers...\n")

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(convert_file, mf): mf for mf in media_files}

        for i, future in enumerate(as_completed(futures), 1):
            input_path, ok, message = future.result()
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            eta = (total - i) / rate if rate > 0 else 0

            if ok:
                success += 1
                status = "OK"
            else:
                failed += 1
                status = "FAIL"

            print(
                f"[{i}/{total}] {status}: {input_path} — {message}  "
                f"({rate:.1f} files/s, ETA {int(eta // 60)}m{int(eta % 60):02d}s)"
            )

    elapsed = time.time() - start_time
    print(f"\nDone in {int(elapsed // 60)}m{int(elapsed % 60):02d}s: "
          f"{success} converted, {failed} failed out of {total}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    # Parse --workers argument
    workers = min(cpu_count(), 8)  # default: min(cpu_cores, 8)
    args = sys.argv[1:]
    if "--workers" in args:
        idx = args.index("--workers")
        workers = int(args[idx + 1])
        args = args[:idx] + args[idx + 2:]

    input_path = args[0]

    if os.path.isdir(input_path):
        media_files = sorted(glob.glob(os.path.join(input_path, "**", "*.media"), recursive=True))
        if not media_files:
            print(f"No .media files found in {input_path}")
            sys.exit(1)

        # Skip files that already have a corresponding .mp4
        if "--force" not in sys.argv:
            before = len(media_files)
            media_files = [
                mf for mf in media_files
                if not os.path.exists(os.path.splitext(mf)[0] + ".mp4")
            ]
            skipped = before - len(media_files)
            if skipped:
                print(f"Skipping {skipped} already converted files (use --force to reconvert)")
            if not media_files:
                print("All files already converted.")
                sys.exit(0)

        batch_convert(media_files, workers)
    else:
        output_path = args[1] if len(args) > 1 else None
        _, ok, message = convert_file(input_path, output_path)
        print(f"{'OK' if ok else 'FAIL'}: {message}")
        if not ok:
            sys.exit(1)


if __name__ == "__main__":
    main()
