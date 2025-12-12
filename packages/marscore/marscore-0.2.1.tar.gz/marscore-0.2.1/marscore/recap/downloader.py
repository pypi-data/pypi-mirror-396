import requests
import threading
from multiprocessing import Pool, Process, Manager, Queue
from functools import partial
import time
import os
import urllib
from typing import List, Dict, Optional, Tuple
import json
import math
import hashlib
import shutil
from urllib.parse import unquote
from datetime import timedelta
import urllib3
import warnings
from urllib3.exceptions import InsecureRequestWarning
import pandas as pd
import pyarrow.parquet as pq
import io
from pathlib import Path
import concurrent.futures
from threading import Semaphore
import signal

# Disable SSL warnings
urllib3.disable_warnings(InsecureRequestWarning)
warnings.filterwarnings('ignore')

"""
Multi-thread Parquet Image Downloader with Robust Resume Support
Author: marscore
Email: marscore@163.com
GitHub: https://github.com/mars-core/
"""


def progress_monitor(progress_queue, total_urls, update_interval=1):
    """
    Independent process to monitor and display progress for all downloads
    """
    progress_data = {}
    last_update_time = 0
    start_time = time.time()

    print(f"Starting progress monitor for {total_urls} parquet files")
    print("=" * 60)

    while True:
        current_time = time.time()

        # Check for new progress updates
        while not progress_queue.empty():
            try:
                update = progress_queue.get_nowait()
                if update.get('type') == 'progress':
                    process_id = update.get('process_id')
                    progress_data[process_id] = update
                elif update.get('type') == 'complete':
                    process_id = update.get('process_id')
                    if process_id in progress_data:
                        progress_data[process_id]['completed'] = True
                        progress_data[process_id]['final_message'] = update.get('message', '')
                elif update.get('type') == 'error':
                    process_id = update.get('process_id')
                    progress_data[process_id] = {
                        'completed': True,
                        'final_message': f"ERROR: {update.get('message', 'Unknown error')}"
                    }
            except:
                pass

        # Update display at regular intervals
        if current_time - last_update_time >= update_interval:
            # Clear screen and re-display everything
            os.system('cls' if os.name == 'nt' else 'clear')

            print(f"=== Parquet Image Downloader Progress Monitor ===")
            print(f"Monitoring {total_urls} parquet files")
            print("=" * 60)

            completed_count = 0
            active_count = 0
            total_images = 0
            downloaded_images = 0
            total_parquet_size = 0
            downloaded_parquet_size = 0

            # Display all processes in order
            for process_id in range(total_urls):
                if process_id in progress_data:
                    data = progress_data[process_id]

                    if data.get('completed', False):
                        completed_count += 1
                        status = "✓ COMPLETED" if "ERROR" not in data.get('final_message', '') else "✗ FAILED"
                        message = data.get('final_message', 'Download completed')
                        print(f"[Parquet {process_id}] {status}: {message}")
                    else:
                        active_count += 1
                        progress_percent = data.get('progress_percent', 0)
                        downloaded = data.get('downloaded_images', 0)
                        total = data.get('total_images', 0)
                        speed = data.get('speed_str', '0 img/s')
                        eta = data.get('eta_str', 'Unknown')
                        filename = data.get('filename', f'parquet_{process_id}')
                        status_msg = data.get('status', 'downloading')

                        if status_msg == 'downloading_parquet':
                            parquet_progress = data.get('parquet_progress_percent', 0)
                            parquet_downloaded = data.get('parquet_downloaded_str', '0B')
                            parquet_total = data.get('parquet_total_str', 'Unknown')
                            parquet_speed = data.get('parquet_speed_str', '0B/s')
                            print(
                                f"[Parquet {process_id}] {filename}: Downloading parquet... {parquet_progress:.1f}% ({parquet_downloaded}/{parquet_total}) {parquet_speed}")
                        elif status_msg == 'parsing_parquet':
                            print(f"[Parquet {process_id}] {filename}: Parsing parquet file...")
                        elif status_msg == 'downloading_images':
                            print(
                                f"[Parquet {process_id}] {filename}: {progress_percent:6.2f}% ({downloaded:>6}/{total:>6}) {speed:>12} ETA: {eta:>8}")
                        elif status_msg == 'resuming_parquet':
                            print(f"[Parquet {process_id}] {filename}: Resuming parquet download...")
                        elif status_msg == 'resuming_images':
                            resume_info = data.get('resume_info', '')
                            print(f"[Parquet {process_id}] {filename}: Resuming image download... {resume_info}")
                        elif status_msg == 'validating_parquet':
                            print(f"[Parquet {process_id}] {filename}: Validating parquet file...")
                        elif status_msg == 'using_local_parquet':
                            print(f"[Parquet {process_id}] {filename}: Using local parquet file...")
                        else:
                            print(f"[Parquet {process_id}] {filename}: {status_msg}")

                    # Accumulate totals
                    total_images += data.get('total_images', 0)
                    downloaded_images += data.get('downloaded_images', 0)
                    total_parquet_size += data.get('parquet_total_bytes', 0)
                    downloaded_parquet_size += data.get('parquet_downloaded_bytes', 0)
                else:
                    active_count += 1
                    print(f"[Parquet {process_id}] Waiting to start...")

            # Calculate elapsed time
            elapsed_time = current_time - start_time
            elapsed_str = format_time_elapsed(elapsed_time)

            print("-" * 60)
            print(f"Active: {active_count}, Completed: {completed_count}, Total: {total_urls}")

            # Parquet download progress
            if total_parquet_size > 0:
                parquet_progress = (downloaded_parquet_size / total_parquet_size * 100) if total_parquet_size > 0 else 0
                print(
                    f"Parquet: {format_size(downloaded_parquet_size)}/{format_size(total_parquet_size)} ({parquet_progress:.1f}%)")

            # Image download progress
            if total_images > 0:
                progress_percent = (downloaded_images / total_images * 100) if total_images > 0 else 0
                print(f"Images: {downloaded_images}/{total_images} ({progress_percent:.1f}%)")
            else:
                print(f"Images: {downloaded_images}/? (Parsing...)")
            print(f"Elapsed Time: {elapsed_str}")

            last_update_time = current_time

            # Check if all downloads are complete
            if completed_count >= total_urls:
                total_elapsed = time.time() - start_time
                total_elapsed_str = format_time_elapsed(total_elapsed)
                print("\n" + "=" * 60)
                print(f"All downloads completed!")
                print(f"Total Images: {downloaded_images}/{total_images}")
                print(f"Total Elapsed Time: {total_elapsed_str}")
                print("=" * 60)
                break

        time.sleep(0.1)


def format_time_elapsed(seconds):
    """Format elapsed time in a human readable way"""
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{minutes} minutes {secs} seconds"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        secs = int(seconds % 60)
        return f"{hours} hours {minutes} minutes {secs} seconds"


def format_size(size_bytes):
    """Format file size in a human readable way"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s:.2f}{size_names[i]}"


def download_parquet_images(args):
    """
    Download images from a single parquet file in separate process
    """
    parquet_url, kwargs, process_index, progress_queue = args
    downloader = ParquetImageDownloader(process_index, progress_queue)
    try:
        result = downloader.download(parquet_url, **kwargs)
        return result
    except Exception as e:
        # Send error message to progress monitor
        if progress_queue:
            progress_queue.put({
                'type': 'error',
                'process_id': process_index,
                'message': str(e)
            })
        return False


class ResumeManager:
    """
    Manager for handling resume functionality for both parquet and image downloads
    """

    def __init__(self, cache_dir, parquet_filename, process_index):
        self.cache_dir = cache_dir
        self.parquet_filename = parquet_filename
        self.process_index = process_index
        self.resume_dir = os.path.join(cache_dir, 'resume')
        os.makedirs(self.resume_dir, exist_ok=True)

    def get_parquet_resume_file(self):
        """Get parquet resume file path - 使用原文件名作为标识"""
        # 使用原文件名作为标识，避免hash变化导致重新下载
        safe_filename = self.parquet_filename.replace('/', '_').replace('\\', '_')
        return os.path.join(self.resume_dir, f"{safe_filename}_parquet_resume.json")

    def get_image_resume_file(self):
        """Get image resume file path - 使用原文件名作为标识"""
        safe_filename = self.parquet_filename.replace('/', '_').replace('\\', '_')
        return os.path.join(self.resume_dir, f"{safe_filename}_image_resume.json")

    def save_parquet_resume_state(self, state):
        """Save parquet download resume state"""
        try:
            resume_file = self.get_parquet_resume_file()
            temp_file = resume_file + '.tmp'

            state['last_update'] = time.time()
            state['parquet_filename'] = self.parquet_filename

            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

            if os.path.exists(resume_file):
                os.remove(resume_file)
            os.rename(temp_file, resume_file)

        except Exception as e:
            print(f"Warning: Failed to save parquet resume state: {e}")

    def load_parquet_resume_state(self):
        """Load parquet download resume state"""
        try:
            resume_file = self.get_parquet_resume_file()
            if not os.path.exists(resume_file):
                return None

            with open(resume_file, 'r', encoding='utf-8') as f:
                state = json.load(f)

            # Check if resume state is for the same file
            if state.get('parquet_filename') != self.parquet_filename:
                return None

            # Check if resume state is too old (more than 7 days)
            last_update = state.get('last_update', 0)
            if time.time() - last_update > 7 * 24 * 3600:  # 7 days
                print("Resume state is too old, starting fresh")
                return None

            return state

        except Exception as e:
            print(f"Warning: Failed to load parquet resume state: {e}")
            return None

    def save_image_resume_state(self, state):
        """Save image download resume state"""
        try:
            resume_file = self.get_image_resume_file()
            temp_file = resume_file + '.tmp'

            state['last_update'] = time.time()
            state['parquet_filename'] = self.parquet_filename

            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

            if os.path.exists(resume_file):
                os.remove(resume_file)
            os.rename(temp_file, resume_file)

        except Exception as e:
            print(f"Warning: Failed to save image resume state: {e}")

    def load_image_resume_state(self):
        """Load image download resume state"""
        try:
            resume_file = self.get_image_resume_file()
            if not os.path.exists(resume_file):
                return None

            with open(resume_file, 'r', encoding='utf-8') as f:
                state = json.load(f)

            # Check if resume state is for the same file
            if state.get('parquet_filename') != self.parquet_filename:
                return None

            # Check if resume state is too old (more than 7 days)
            last_update = state.get('last_update', 0)
            if time.time() - last_update > 7 * 24 * 3600:  # 7 days
                print("Resume state is too old, starting fresh")
                return None

            return state

        except Exception as e:
            print(f"Warning: Failed to load image resume state: {e}")
            return None

    def cleanup_resume_files(self):
        """Clean up resume files after successful completion"""
        try:
            parquet_resume = self.get_parquet_resume_file()
            image_resume = self.get_image_resume_file()

            if os.path.exists(parquet_resume):
                os.remove(parquet_resume)
            if os.path.exists(image_resume):
                os.remove(image_resume)

        except Exception as e:
            print(f"Warning: Failed to cleanup resume files: {e}")


class ParquetDownloadManager:
    """
    Manager for downloading parquet files with robust resume support
    """

    def __init__(self, process_index=0, progress_queue=None):
        self.process_index = process_index
        self.progress_queue = progress_queue
        self.parquet_url = ""
        self.parquet_filename = ""
        self.local_parquet_path = ""
        self.cache_dir = ""
        self.resume_manager = None
        self.is_downloading = True

    def send_progress_update(self, progress_data):
        """Send progress update to monitor process"""
        if self.progress_queue and self.is_downloading:
            try:
                progress_data['type'] = 'progress'
                progress_data['process_id'] = self.process_index
                progress_data['timestamp'] = time.time()
                self.progress_queue.put(progress_data)
            except:
                pass

    def validate_parquet_file(self, file_path):
        """Validate parquet file integrity"""
        try:
            # Check file size first
            file_size = os.path.getsize(file_path)
            if file_size < 100:
                return False, "File too small to be a valid parquet file"

            # Try to read with pandas
            df = pd.read_parquet(file_path)
            return True, df
        except Exception as e:
            return False, str(e)

    def is_local_file(self, path):
        """Check if the path is a local file"""
        if path.startswith(('http://', 'https://')):
            return False
        return os.path.exists(path)

    def get_parquet_file(self, parquet_url, cache_dir):
        """
        Get parquet file - handles both local files and remote URLs
        Returns local file path
        """
        self.parquet_url = parquet_url
        self.parquet_filename = self.get_filename_from_url(parquet_url)
        self.cache_dir = cache_dir

        # Initialize resume manager
        self.resume_manager = ResumeManager(cache_dir, self.parquet_filename, self.process_index)

        # Create data directory
        os.makedirs(cache_dir, exist_ok=True)

        # Generate local filename - 使用原文件名，不加hash前缀
        local_filename = self.parquet_filename
        local_path = os.path.join(cache_dir, local_filename)

        # Check if it's a local file
        if self.is_local_file(parquet_url):
            print(f"Using local parquet file: {parquet_url}")
            self.send_progress_update({
                'status': 'using_local_parquet',
                'filename': self.parquet_filename
            })

            # Validate local file
            is_valid, error = self.validate_parquet_file(parquet_url)
            if is_valid:
                return parquet_url
            else:
                raise Exception(f"Local parquet file is invalid: {error}")

        # It's a remote URL, proceed with download
        temp_path = local_path + '.tmp'

        # Check if already cached and valid
        if os.path.exists(local_path):
            is_valid, error = self.validate_parquet_file(local_path)
            if is_valid:
                print(f"Using cached parquet file: {local_path}")
                return local_path

        # Get remote file size
        remote_size = self.get_remote_file_size(parquet_url)
        print(f"Downloading {self.parquet_filename} ({format_size(remote_size)})")

        # Load resume state
        resume_state = self.resume_manager.load_parquet_resume_state()

        downloaded_size = 0
        if resume_state and os.path.exists(temp_path):
            downloaded_size = os.path.getsize(temp_path)
            print(f"Resuming download from {format_size(downloaded_size)}")
            self.send_progress_update({
                'status': 'resuming_parquet',
                'filename': self.parquet_filename
            })

        max_retries = 3
        for attempt in range(max_retries):
            if not self.is_downloading:
                break

            try:
                headers = {}
                if downloaded_size > 0:
                    headers['Range'] = f'bytes={downloaded_size}-'

                # Send initial progress update
                self.send_progress_update({
                    'status': 'downloading_parquet',
                    'filename': self.parquet_filename,
                    'parquet_progress_percent': 0,
                    'parquet_downloaded_str': format_size(downloaded_size),
                    'parquet_total_str': format_size(remote_size) if remote_size > 0 else 'Unknown',
                    'parquet_speed_str': '0B/s'
                })

                response = requests.get(parquet_url, headers=headers, verify=False, timeout=120, stream=True)
                response.raise_for_status()

                # Check if we're getting actual data
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' in content_type:
                    content_sample = response.content[:500]
                    if b'<html' in content_sample.lower():
                        raise Exception("Server returned HTML instead of parquet data")

                # Get total size for progress tracking
                total_size = remote_size
                if 'content-length' in response.headers:
                    content_length = response.headers['content-length']
                    if content_length:
                        if headers:  # Resuming download
                            total_size = downloaded_size + int(content_length)
                        else:
                            total_size = int(content_length)

                mode = 'ab' if downloaded_size > 0 else 'wb'
                start_time = time.time()
                last_update_time = start_time
                last_save_time = start_time

                with open(temp_path, mode) as f:
                    chunk_count = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if not self.is_downloading:
                            break

                        if chunk:
                            f.write(chunk)
                            f.flush()
                            downloaded_size += len(chunk)
                            chunk_count += 1

                            # Save resume state every 10 seconds
                            current_time = time.time()
                            if current_time - last_save_time >= 10:
                                resume_state = {
                                    'downloaded_size': downloaded_size,
                                    'total_size': total_size
                                }
                                self.resume_manager.save_parquet_resume_state(resume_state)
                                last_save_time = current_time

                            # Update progress every 0.5 seconds or every 100 chunks
                            if current_time - last_update_time >= 0.5 or chunk_count % 100 == 0:
                                progress_percent = (downloaded_size / total_size * 100) if total_size > 0 else 0
                                elapsed_time = current_time - start_time
                                speed = downloaded_size / elapsed_time if elapsed_time > 0 else 0

                                self.send_progress_update({
                                    'status': 'downloading_parquet',
                                    'filename': self.parquet_filename,
                                    'parquet_progress_percent': progress_percent,
                                    'parquet_downloaded_str': format_size(downloaded_size),
                                    'parquet_total_str': format_size(total_size),
                                    'parquet_speed_str': f"{format_size(speed)}/s",
                                    'parquet_downloaded_bytes': downloaded_size,
                                    'parquet_total_bytes': total_size
                                })
                                last_update_time = current_time

                if not self.is_downloading:
                    # Save resume state before exiting
                    resume_state = {
                        'downloaded_size': downloaded_size,
                        'total_size': total_size
                    }
                    self.resume_manager.save_parquet_resume_state(resume_state)
                    raise Exception("Download was interrupted")

                # Validate downloaded file
                self.send_progress_update({
                    'status': 'validating_parquet',
                    'filename': self.parquet_filename
                })

                is_valid, error = self.validate_parquet_file(temp_path)
                if not is_valid:
                    # Remove invalid file
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                    raise Exception(f"Downloaded file is not a valid parquet file: {error}")

                # Rename to final file
                os.rename(temp_path, local_path)

                # Clean up resume state
                self.resume_manager.cleanup_resume_files()

                print(f"Successfully downloaded and validated: {local_path}")
                return local_path

            except Exception as e:
                print(f"Download attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 * (attempt + 1)
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)

                    # Update downloaded_size for next attempt
                    if os.path.exists(temp_path):
                        downloaded_size = os.path.getsize(temp_path)
                    else:
                        downloaded_size = 0
                else:
                    # Save resume state on final failure
                    resume_state = {
                        'downloaded_size': downloaded_size,
                        'total_size': total_size if 'total_size' in locals() else 0
                    }
                    self.resume_manager.save_parquet_resume_state(resume_state)
                    raise Exception(f"Failed to download parquet file after {max_retries} attempts: {str(e)}")

        raise Exception("Download failed after all retries")

    def stop_download(self):
        """Stop the download process"""
        self.is_downloading = False

    def get_filename_from_url(self, url):
        """Extract filename from URL or local path"""
        try:
            # Check if it's a URL
            if url.startswith(('http://', 'https://')):
                parsed = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed.path)
                if not filename:
                    filename = "unknown.parquet"
                return filename
            else:
                # It's a local path
                return os.path.basename(url)
        except:
            return "unknown.parquet"

    def get_remote_file_size(self, url):
        """Get remote file size using HEAD request"""
        try:
            # If it's a local file, return file size
            if self.is_local_file(url):
                return os.path.getsize(url)

            # It's a remote URL
            response = requests.head(url, verify=False, timeout=30)
            response.raise_for_status()
            content_length = response.headers.get('content-length')
            if content_length:
                return int(content_length)
            return 0
        except:
            return 0


class ParquetImageDownloader:
    """
    Downloader for images from a single parquet file with robust resume support
    """

    def __init__(self, process_index=0, progress_queue=None):
        self.process_index = process_index
        self.progress_queue = progress_queue
        self.parquet_url = ""
        self.parquet_filename = ""
        self.local_parquet_path = ""
        self.output_dir = ""
        self.log_dir = ""
        self.progress_file = ""
        self.metadata_file = ""
        self.threads = []
        self.image_data = []  # Store both URL and row index
        self.total_images = 0
        self.downloaded_images = 0
        self.failed_images = 0
        self.current_index = 0
        self.is_downloading = False
        self.start_time = 0
        self.last_update_time = 0
        self.last_downloaded = 0
        self.current_speed = 0
        self.num_threads = 10
        self.max_retries = 3
        self.retry_count = 0
        self.parquet_downloader = None
        self.resume_manager = None

        # Initialize locks
        self.lock = threading.Lock()
        self.progress_lock = threading.Lock()
        self.metadata_lock = threading.Lock()
        self.print_lock = threading.Lock()

    def send_progress_update(self, progress_data):
        """Send progress update to monitor process"""
        if self.progress_queue and self.is_downloading:
            try:
                progress_data['type'] = 'progress'
                progress_data['process_id'] = self.process_index
                progress_data['timestamp'] = time.time()
                self.progress_queue.put(progress_data)
            except:
                pass

    def send_completion_update(self, message):
        """Send completion update to monitor process"""
        if self.progress_queue:
            try:
                self.progress_queue.put({
                    'type': 'complete',
                    'process_id': self.process_index,
                    'message': message,
                    'timestamp': time.time()
                })
            except:
                pass

    def send_error_update(self, message):
        """Send error update to monitor process"""
        if self.progress_queue:
            try:
                self.progress_queue.put({
                    'type': 'error',
                    'process_id': self.process_index,
                    'message': message,
                    'timestamp': time.time()
                })
            except:
                pass

    def get_parquet_file(self, parquet_url, cache_dir):
        """
        Get parquet file - handles both local files and remote URLs
        """
        self.send_progress_update({
            'status': 'downloading_parquet',
            'filename': self.parquet_filename
        })

        # Initialize parquet downloader
        self.parquet_downloader = ParquetDownloadManager(
            process_index=self.process_index,
            progress_queue=self.progress_queue
        )

        # Get parquet file (download if remote, use directly if local)
        local_path = self.parquet_downloader.get_parquet_file(parquet_url, cache_dir)

        return local_path

    def load_parquet(self, parquet_path):
        """
        Load parquet file and extract image URLs with row indices

        Returns:
            List of tuples (row_index, image_url)
        """
        self.send_progress_update({
            'status': 'parsing_parquet',
            'filename': self.parquet_filename
        })

        try:
            # Read parquet file
            df = pd.read_parquet(parquet_path)

            # Extract image URLs with row indices - try common column names
            image_data = []

            # Common column names that might contain URLs
            url_columns = ['url', 'image_url', 'img_url', 'path', 'image_path', 'file_path',
                           'URL', 'image_URL', 'img_URL', 'PATH', 'image_PATH', 'image', 'img']

            # First pass: check specific column names
            for col in df.columns:
                col_lower = col.lower()
                # Check if column name suggests it contains URLs
                if any(keyword in col_lower for keyword in ['url', 'image', 'img', 'path', 'link']):
                    # Try to extract URLs from this column with row indices
                    for row_idx, url in enumerate(df[col]):
                        if pd.notna(url):
                            url_str = str(url).strip()
                            if url_str.startswith(('http://', 'https://')):
                                image_data.append((row_idx, url_str))

            # Second pass: if no URLs found, check all string columns
            if not image_data:
                for col in df.select_dtypes(include=['object']).columns:
                    for row_idx, url in enumerate(df[col]):
                        if pd.notna(url):
                            url_str = str(url).strip()
                            if url_str.startswith(('http://', 'https://')):
                                image_data.append((row_idx, url_str))

            # Remove duplicates while preserving order
            seen = set()
            unique_image_data = []
            for row_idx, url in image_data:
                if url not in seen:
                    seen.add(url)
                    unique_image_data.append((row_idx, url))

            print(f"Found {len(unique_image_data)} unique image URLs in parquet file")
            return unique_image_data

        except Exception as e:
            raise Exception(f"Failed to parse parquet file: {str(e)}")

    def get_filename_from_url(self, url):
        """Extract filename from URL or local path"""
        try:


            # Check if it's a URL
            if url.startswith(('http://', 'https://')):
                parsed = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed.path)
                if not filename:
                    filename = "unknown.parquet"
                return filename
            else:
                # It's a local path
                return os.path.basename(url)
        except:
            return "unknown.parquet"

    def generate_unique_filename(self, directory, filename):
        """Generate unique filename using hash fingerprint"""
        name, ext = os.path.splitext(filename)
        if not ext:
            ext = '.jpg'  # default extension

        base_path = os.path.join(directory, filename)

        # If file doesn't exist, use original name
        if not os.path.exists(base_path):
            return filename

        # Generate unique name with hash
        file_hash = hashlib.md5(f"{directory}/{filename}".encode()).hexdigest()[:30]
        unique_name = f"{name}_{file_hash}{ext}"

        return unique_name

    def save_image_metadata(self, row_index, output_filename, success=True):
        """Save image metadata to JSON file (per parquet file)"""
        if not self.metadata_lock.acquire(blocking=False):
            return

        try:
            metadata_entry = {
                "parquet": self.parquet_filename,
                "parquet_row": row_index,
                "output_filename": output_filename,
                "download_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "success": success
            }

            # Load existing metadata for this parquet file
            metadata = []
            if os.path.exists(self.metadata_file):
                try:
                    with open(self.metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                except:
                    metadata = []

            # Add new entry
            metadata.append(metadata_entry)

            # Save back to file
            temp_file = self.metadata_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            if os.path.exists(self.metadata_file):
                os.remove(self.metadata_file)
            os.rename(temp_file, self.metadata_file)

        except Exception as e:
            pass
        finally:
            self.metadata_lock.release()

    def download_single_image(self, row_index, url, output_dir, retry_count=0):
        """Download a single image with retry logic and metadata recording"""
        if retry_count >= self.max_retries:
            self.save_image_metadata(row_index, "", success=False)
            return False

        try:
            # Get filename from URL
            # filename = self.get_filename_from_url(url)
            filename = f"image_{hashlib.md5(url.encode()).hexdigest()[:30]}.jpg"
            if not filename or '.' not in filename:
                filename = f"image_{hashlib.md5(url.encode()).hexdigest()[:8]}.jpg"

            # # Generate unique filename if needed
            unique_filename = self.generate_unique_filename(output_dir, filename)


            filepath = os.path.join(output_dir, unique_filename)

            # Skip if already downloaded
            if os.path.exists(filepath):
                self.save_image_metadata(row_index, unique_filename, success=True)
                return True

            # Download image
            response = requests.get(url, timeout=30, verify=False, stream=True)
            response.raise_for_status()

            # Check if response is actually an image
            content_type = response.headers.get('content-type', '').lower()
            if not any(img_type in content_type for img_type in ['image', 'jpeg', 'jpg', 'png', 'gif', 'webp']):
                # Not an image, skip
                return False

            # Save image
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # Record successful download metadata
            self.save_image_metadata(row_index, unique_filename, success=True)
            return True

        except Exception as e:
            if retry_count < self.max_retries - 1:
                time.sleep(1)
                return self.download_single_image(row_index, url, output_dir, retry_count + 1)
            else:
                self.save_image_metadata(row_index, "", success=False)
                return False

    def download_image_batch(self, thread_id, batch_data, output_dir):
        """Download a batch of images in a single thread"""
        successful = 0
        failed = 0

        for row_index, url in batch_data:
            if not self.is_downloading:
                break

            if self.download_single_image(row_index, url, output_dir):
                successful += 1
            else:
                failed += 1

            # Update progress
            with self.lock:
                self.downloaded_images += 1
                self.current_index += 1

        return successful, failed

    def save_progress(self):
        """Save download progress to JSON file"""
        if not self.progress_lock.acquire(blocking=False):
            return

        try:
            progress_data = {
                "parquet_url": self.parquet_url,
                "parquet_filename": self.parquet_filename,
                "local_parquet_path": self.local_parquet_path,
                "total_images": self.total_images,
                "downloaded_images": self.downloaded_images,
                "current_index": self.current_index,
                "failed_images": self.failed_images,
                "image_data_count": len(self.image_data),
                "timestamp": time.time()
            }

            temp_file = self.progress_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2, ensure_ascii=False)

            if os.path.exists(self.progress_file):
                os.remove(self.progress_file)
            os.rename(temp_file, self.progress_file)

        except Exception as e:
            pass
        finally:
            self.progress_lock.release()

    def load_progress(self):
        """Load download progress from JSON file"""
        try:
            if not os.path.exists(self.progress_file):
                return False

            with open(self.progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Verify that we're loading progress for the same parquet file
            if data.get("parquet_url") != self.parquet_url:
                print(f"Progress file mismatch: {data.get('parquet_url')} vs {self.parquet_url}")
                return False

            self.downloaded_images = data.get("downloaded_images", 0)
            self.current_index = data.get("current_index", 0)
            self.failed_images = data.get("failed_images", 0)
            self.total_images = data.get("total_images", 0)

            # Verify that the parquet file still exists
            local_path = data.get("local_parquet_path")
            if local_path and os.path.exists(local_path):
                self.local_parquet_path = local_path
                print(f"Resuming from progress: {self.downloaded_images}/{self.total_images} images downloaded")
                return True
            else:
                print("Local parquet file not found, cannot resume")
                return False

        except Exception as e:
            print(f"Error loading progress: {e}")
            return False

    def update_speed_stats(self, current_downloaded, current_time):
        """Update download speed statistics"""
        if self.last_update_time == 0:
            self.last_update_time = current_time
            self.last_downloaded = current_downloaded
            return

        time_diff = current_time - self.last_update_time
        if time_diff >= 1.0:
            downloaded_diff = current_downloaded - self.last_downloaded
            self.current_speed = downloaded_diff / time_diff
            self.last_update_time = current_time
            self.last_downloaded = current_downloaded

    def format_speed(self, speed):
        """Format speed display"""
        if speed <= 0:
            return "0 img/s"
        return f"{speed:.1f} img/s"

    def format_eta(self, remaining, speed):
        """Calculate and format estimated remaining time"""
        if speed <= 0 or remaining <= 0:
            return "Unknown"

        seconds = remaining / speed
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds / 60)}m{int(seconds % 60)}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h{minutes}m"

    def download(self, parquet_url, **kwargs):
        """
        Main download method for parquet file with robust resume support
        """
        self.max_retries = kwargs.get('retry_num', 3)
        self.retry_count = 0
        self.num_threads = kwargs.get('threads', 20)

        # Set up signal handler for graceful interruption
        def signal_handler(signum, frame):
            print(f"\nProcess {self.process_index} received interrupt signal, saving state...")
            self.is_downloading = False
            if self.parquet_downloader:
                self.parquet_downloader.stop_download()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        while self.retry_count <= self.max_retries:
            try:
                # Initialize downloader
                self._init_downloader_attributes(parquet_url, kwargs)

                # Initialize resume manager
                cache_dir = kwargs.get('cache_dir', 'parquet_cache')
                self.resume_manager = ResumeManager(cache_dir, self.parquet_filename, self.process_index)

                # Send initial progress update
                self.send_progress_update({
                    'filename': self.parquet_filename,
                    'progress_percent': 0,
                    'downloaded_images': 0,
                    'total_images': 0,
                    'speed_str': '0 img/s',
                    'eta_str': 'Unknown',
                    'status': 'initializing'
                })

                # Create directories
                self._create_directories()

                if self.retry_count > 0:
                    self.send_progress_update({
                        'status': f'retry_{self.retry_count}'
                    })

                # Step 1: Get parquet file (download if remote, use directly if local)
                print(f"Processing parquet file: {self.parquet_filename}")
                self.local_parquet_path = self.get_parquet_file(parquet_url, cache_dir)

                # Step 2: Parse parquet file to get image URLs with row indices
                self.image_data = self.load_parquet(self.local_parquet_path)
                self.total_images = len(self.image_data)

                if self.total_images == 0:
                    raise Exception("No image URLs found in parquet file")

                # Update progress with actual count
                self.send_progress_update({
                    'total_images': self.total_images,
                    'status': 'parsing_complete'
                })

                # Step 3: Check if previous download progress exists
                resume = os.path.exists(self.progress_file) and self.load_progress()
                if resume:
                    resume_info = f"({self.downloaded_images}/{self.total_images} images)"
                    self.send_progress_update({
                        'status': 'resuming_images',
                        'resume_info': resume_info
                    })

                # Step 4: Start downloading images with multi-threading
                print(f"Starting image download with {self.num_threads} threads...")
                result = self.start_download(resume=resume)

                if result:
                    # Create summary file for this parquet
                    self.create_download_summary()

                    # Clean up resume files
                    self.resume_manager.cleanup_resume_files()

                    self.send_completion_update(
                        f"Completed: {self.downloaded_images}/{self.total_images} images "
                        f"({self.failed_images} failed)"
                    )
                    return True
                else:
                    self.retry_count += 1
                    if self.retry_count <= self.max_retries:
                        wait_time = 2 * self.retry_count
                        self.send_progress_update({
                            'status': f'waiting_retry_{self.retry_count}',
                            'wait_time': wait_time
                        })
                        time.sleep(wait_time)
                    else:
                        self.send_error_update(
                            f"Failed after {self.max_retries} retries: "
                            f"{self.downloaded_images}/{self.total_images} images"
                        )
                        return False

            except Exception as e:
                self.retry_count += 1
                if self.retry_count <= self.max_retries:
                    wait_time = 2 * self.retry_count
                    self.send_progress_update({
                        'status': f'error_retry_{self.retry_count}: {str(e)}',
                        'wait_time': wait_time
                    })
                    time.sleep(wait_time)
                else:
                    self.send_error_update(f"Failed after {self.max_retries} retries: {str(e)}")
                    return False

        return False

    def create_download_summary(self):
        """Create a summary file for this parquet download"""
        try:
            summary_data = {
                "parquet_filename": self.parquet_filename,
                "total_images": self.total_images,
                "successful_downloads": self.downloaded_images - self.failed_images,
                "failed_downloads": self.failed_images,
                "download_completion_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "output_directory": self.output_dir,
                "metadata_file": self.metadata_file
            }

            summary_file = os.path.join(self.output_dir, "download_summary.json")
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            pass

    def _init_downloader_attributes(self, parquet_url, kwargs):
        """Initialize downloader attributes"""
        self.parquet_url = parquet_url
        self.parquet_filename = self.get_filename_from_url(parquet_url)
        self.num_threads = kwargs.get('threads', 20)
        self.max_retries = kwargs.get('retry_num', 3)

        # Set output directories
        base_output_dir = kwargs.get('output_dir', 'parquet_images')
        self.output_dir = f"{base_output_dir}/{os.path.splitext(self.parquet_filename)[0]}"
        self.log_dir = f"{base_output_dir}/logs"

        # Set progress file and metadata file (per parquet file)
        self.progress_file = f"{self.log_dir}/{self.parquet_filename}_progress.json"
        self.metadata_file = f"{self.output_dir}/down_images.json"

        # Initialize statistics
        self.image_data = []
        self.total_images = 0
        self.downloaded_images = 0
        self.failed_images = 0
        self.current_index = 0
        self.is_downloading = True  # Start as True
        self.start_time = 0
        self.last_update_time = 0
        self.last_downloaded = 0
        self.current_speed = 0
        self.local_parquet_path = ""

    def _create_directories(self):
        """Create necessary directories"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

    def start_download(self, resume=False):
        """Start downloading images from parquet"""
        try:
            self.is_downloading = True
            self.start_time = time.time()
            self.last_update_time = 0
            self.last_downloaded = 0
            self.current_speed = 0

            # If resuming, skip already downloaded images
            start_index = self.current_index if resume else 0
            remaining_data = self.image_data[start_index:]

            if not remaining_data:
                # All images already downloaded
                print(f"All images already downloaded for {self.parquet_filename}")
                return True

            print(f"Starting download from index {start_index}, {len(remaining_data)} images remaining")

            # Split remaining data into batches for threads
            batch_size = max(1, len(remaining_data) // self.num_threads)
            batches = []
            for i in range(0, len(remaining_data), batch_size):
                batches.append(remaining_data[i:i + batch_size])

            # Start download threads
            download_threads = []
            for i, batch in enumerate(batches):
                thread = threading.Thread(
                    target=self.download_image_batch,
                    args=(i, batch, self.output_dir),
                    daemon=True
                )
                download_threads.append(thread)
                thread.start()

            # Monitor progress
            return self.monitor_progress(download_threads)

        except Exception as e:
            self.is_downloading = False
            print(f"Error starting download: {e}")
            return False

    def monitor_progress(self, download_threads):
        """Monitor download progress"""
        try:
            last_save_time = time.time()
            last_progress_update = 0

            while any(thread.is_alive() for thread in download_threads) and self.is_downloading:
                current_time = time.time()

                # Update speed statistics
                self.update_speed_stats(self.downloaded_images, current_time)

                # Periodically save progress
                if current_time - last_save_time >= 5:  # Save every 5 seconds
                    self.save_progress()
                    last_save_time = current_time

                # Periodically send progress update
                if current_time - last_progress_update >= 1:  # Update every 1 second
                    progress_percent = (
                            self.downloaded_images / self.total_images * 100) if self.total_images > 0 else 0

                    # Calculate ETA
                    remaining_images = self.total_images - self.downloaded_images
                    eta_str = self.format_eta(remaining_images, self.current_speed)

                    # Format speed
                    speed_str = self.format_speed(self.current_speed)

                    # Send progress update
                    self.send_progress_update({
                        'filename': self.parquet_filename,
                        'progress_percent': progress_percent,
                        'downloaded_images': self.downloaded_images,
                        'total_images': self.total_images,
                        'speed_str': speed_str,
                        'eta_str': eta_str,
                        'status': 'downloading_images'
                    })

                    last_progress_update = current_time

                time.sleep(0.1)

            # Wait for all threads to complete
            for thread in download_threads:
                thread.join(timeout=5)

            # Final progress save
            if self.is_downloading:
                self.save_progress()
                # Clean up progress file if download completed successfully
                if self.downloaded_images >= self.total_images:
                    try:
                        if os.path.exists(self.progress_file):
                            os.remove(self.progress_file)
                            print(f"Cleaned up progress file: {self.progress_file}")
                    except:
                        pass
                return True
            else:
                self.save_progress()
                print("Download was interrupted, progress saved")
                return False

        except KeyboardInterrupt:
            self.is_downloading = False
            self.save_progress()
            print("Download interrupted, progress saved")
            return False
        except Exception as e:
            self.is_downloading = False
            self.save_progress()
            print(f"Error monitoring progress: {e}")
            return False


class MultiParquetDownloader:
    """
    Main downloader class for multiple parquet files
    """

    def __init__(self):
        pass

    def run(self, urls, **kwargs):
        """
        Run downloader with multiple processes

        Args:
            urls: List of parquet URLs or local file paths
            **kwargs: Additional parameters

        Returns:
            List of download results
        """
        if isinstance(urls, str):
            urls = [urls]

        num_process = kwargs.get('process', min(len(urls), 10))
        num_process = min(len(urls), num_process)

        print(f"Starting {num_process} processes for {len(urls)} parquet files")
        print(
            f"Each process will use single-threaded parquet download and {kwargs.get('threads', 20)} threads for image downloading")
        print("Supports both local parquet files and remote URLs")
        print("Resume support is enabled - interrupted downloads will continue from where they left off")

        # Create progress queue for communication with monitor
        manager = Manager()
        progress_queue = manager.Queue()

        # Start progress monitor process
        monitor_process = Process(
            target=progress_monitor,
            args=(progress_queue, len(urls), 1)
        )
        monitor_process.start()

        # Give monitor process time to initialize display
        time.sleep(0.5)

        # Prepare arguments for each parquet file with process index
        download_args = []
        for i, url in enumerate(urls):
            download_args.append((url, kwargs, i, progress_queue))

        # Create process pool
        with Pool(processes=num_process) as pool:
            results = pool.map(download_parquet_images, download_args)

        # Wait for monitor process to finish
        monitor_process.join(timeout=10)
        if monitor_process.is_alive():
            monitor_process.terminate()

        # Check for incomplete downloads and retry if needed
        successful_count = sum(results)
        if successful_count < len(results):
            print(f"\nSome downloads failed. {successful_count} successful out of {len(results)}")
            print("You can rerun the same command to resume interrupted downloads")

        print(f"\nAll downloads completed. Results: {successful_count} successful out of {len(results)}")
        return results


def recap(url, process=10, threads=20, output_dir='output/parquet_images', retry_num=3, cache_dir='output/parquet_cache'):
    """
    Main function for downloading images from parquet files with robust resume support

    Args:
        url: List of parquet URLs or local file paths
        process: Number of processes to use (default: 10)
        threads: Number of threads per parquet file for image download (default: 20)
        output_dir: Output directory for images
        retry_num: Number of retries for failed downloads
        cache_dir: Directory for caching downloaded parquet files and resume data

    Returns:
        List of download results
    """
    downloader = MultiParquetDownloader()
    results = downloader.run(
        urls=url,
        process=process,
        threads=threads,
        output_dir=output_dir,
        retry_num=retry_num,
        cache_dir=cache_dir
    )
    return results


def main():
    """Main function for testing"""
    # Test with both local and remote parquet files
    test_urls = [
        # Remote URL
        'https://huggingface.co/datasets/UCSC-VLAA/Recap-DataComp-1B/resolve/main/data/train_data/train-00001-of-04627.parquet',
        # Local file (if exists)
        # '/path/to/local/file.parquet'
    ]

    results = recap(
        url='train-00001-of-04627.parquet',
        process=2,  # Use 2 processes for testing
        threads=4  # 4 threads for testing
    )

    print(f"All downloads completed. Results: {sum(results)} successful out of {len(results)}")


if __name__ == "__main__":
    main()