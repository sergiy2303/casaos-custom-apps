import os
import re
import subprocess
import datetime
import argparse
import csv
import sys

def process_videos(base_dir, batch_size=5000):
    # Regex to match the timestamp folder pattern like 1756868519_0060
    pattern = re.compile(r'^(\d{10})_')

    target_files = []

    print(f"Scanning directory: {base_dir} ...")

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith('.mp4'):
                file_path = os.path.join(root, file)

                # Extract timestamp from the directory name
                parent_dir = os.path.basename(root)
                match = pattern.match(parent_dir)

                if match:
                    timestamp = int(match.group(1))
                    target_files.append((file_path, timestamp))

    total_files = len(target_files)
    print(f"Found {total_files} videos with timestamped folders.")

    if total_files == 0:
        return

    # Check for exiftool
    exiftool_installed = True
    try:
        subprocess.run(["exiftool", "-ver"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: 'exiftool' is not installed or not in PATH.")
        print("The script will only update file system creation/modification times.")
        print("To also update internal video metadata (highly recommended for PhotoPrism), install exiftool:")
        print("  Ubuntu/Debian: sudo apt-get install libimage-exiftool-perl")
        exiftool_installed = False

    csv_count = 0

    # Process in batches to avoid high memory/CPU usage for 120k files
    for i in range(0, total_files, batch_size):
        batch = target_files[i:i+batch_size]
        csv_filename = f"/tmp/exiftool_batch_{csv_count}.csv"

        with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Standard QuickTime metadata headers for EXIFTool
            writer.writerow([
                "SourceFile",
                "CreateDate",
                "ModifyDate",
                "TrackCreateDate",
                "TrackModifyDate",
                "MediaCreateDate",
                "MediaModifyDate"
            ])

            for file_path, timestamp in batch:
                # 1. Update file system times immediately (fallback for PhotoPrism)
                try:
                    os.utime(file_path, (timestamp, timestamp))
                except Exception as e:
                    pass # Ignore permissions or missing file errors if any

                # 2. Prepare metadata for exiftool
                # Convert to UTC string formatted for EXIFTool (YYYY:MM:DD HH:MM:SS)
                dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
                formatted_time = dt.strftime("%Y:%m:%d %H:%M:%S")

                writer.writerow([
                    file_path,
                    formatted_time,
                    formatted_time,
                    formatted_time,
                    formatted_time,
                    formatted_time,
                    formatted_time
                ])

        # Run exiftool for this batch
        if exiftool_installed:
            print(f"Updating internal metadata for batch {csv_count+1} (files {i+1} to {min(i+batch_size, total_files)})...")
            cmd = [
                "exiftool",
                "-overwrite_original", # Don't leave "_original" backup files around
                "-m",                  # ignore minor errors
                f"-csv={csv_filename}"
            ]

            # Create arguments file to avoid OS command line length limit for thousands of files
            args_filename = f"/tmp/exiftool_args_{csv_count}.txt"
            with open(args_filename, "w", encoding="utf-8") as args_file:
                for file_path, _ in batch:
                    args_file.write(f"{file_path}\n")

            cmd.append(f"-@")
            cmd.append(args_filename)

            # Run exiftool
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error running exiftool on batch {csv_count+1}: {e}")

            # Cleanup temp files
            try:
                os.remove(args_filename)
                os.remove(csv_filename)
            except:
                pass

        csv_count += 1

    print("\n--- Summary ---")
    print(f"Successfully processed {total_files} files.")
    if not exiftool_installed:
        print("Note: Only file system timestamps were updated.")
        print("For PhotoPrism, updating internal EXIF metadata is strongly recommended.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update video metadata based on folder timestamp for PhotoPrism.")
    parser.add_argument("directory", help="The base directory to scan (e.g., /DATA/Gallery/Camera)")
    parser.add_argument("--batch-size", type=int, default=5000, help="Number of files to process per exiftool batch (default 5000)")
    args = parser.parse_args()

    process_videos(args.directory, args.batch_size)
