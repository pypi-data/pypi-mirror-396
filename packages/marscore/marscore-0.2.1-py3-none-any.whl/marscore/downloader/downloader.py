import requests
import threading
from multiprocessing import Pool, Process, Manager, Queue
from functools import partial
import time
import os
import urllib
from typing import List, Dict, Optional
import json
import math
import hashlib
import shutil
from urllib.parse import unquote
from datetime import timedelta
import urllib3
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
urllib3.disable_warnings(InsecureRequestWarning)
# Or disable all warnings
warnings.filterwarnings('ignore')

"""
Multi-thread Downloader
Author: marscore
Email: marscore@163.com
GitHub: https://github.com/mars-core/
"""


def progress_monitor(progress_queue, total_urls, update_interval=1):
    """
    Independent process to monitor and display progress for all downloads
    Simple approach without complex cursor movement
    """
    progress_data = {}
    last_update_time = 0
    start_time = time.time()

    print(f"Starting progress monitor for {total_urls} URLs")
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
            except:
                pass

        # Update display at regular intervals
        if current_time - last_update_time >= update_interval:
            # Clear screen and re-display everything
            os.system('cls' if os.name == 'nt' else 'clear')

            print(f"=== Multi-thread Downloader Progress Monitor ===")
            print(f"Monitoring {total_urls} URLs")
            print("=" * 60)

            completed_count = 0
            active_count = 0

            # Display all processes in order
            for process_id in range(total_urls):
                if process_id in progress_data:
                    data = progress_data[process_id]

                    if data.get('completed', False):
                        completed_count += 1
                        status = "✓ COMPLETED"
                        message = data.get('final_message', 'Download completed')
                        print(f"[Process {process_id}] {status}: {message}")
                    else:
                        active_count += 1
                        progress_percent = data.get('progress_percent', 0)
                        downloaded = data.get('downloaded_str', '0B')
                        total = data.get('total_str', 'Unknown')
                        speed = data.get('speed_str', '0 B/s')
                        eta = data.get('eta_str', 'Unknown')

                        print(
                            f"[Process {process_id}] {progress_percent:6.2f}% ({downloaded:>8}/{total:>8}) {speed:>10} ETA: {eta:>8}")
                else:
                    active_count += 1
                    print(f"[Process {process_id}] Waiting to start...")

            # Calculate elapsed time
            elapsed_time = current_time - start_time
            elapsed_str = format_time_elapsed(elapsed_time)

            print("-" * 60)
            print(f"Active: {active_count}, Completed: {completed_count}, Total: {total_urls}")
            print(f"Elapsed Time: {elapsed_str}")

            last_update_time = current_time

            # Check if all downloads are complete
            if completed_count >= total_urls:
                total_elapsed = time.time() - start_time
                total_elapsed_str = format_time_elapsed(total_elapsed)
                print("\n" + "=" * 60)
                print(f"All downloads completed!")
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


def download_single_url(args):
    """
    Download single URL in separate process
    This is a module-level function that can be pickled

    Args:
        args: Tuple of (url, kwargs, process_index, progress_queue)

    Returns:
        Download result
    """
    url, kwargs, process_index, progress_queue = args
    downloader = SingleURLDownloader(process_index, progress_queue)
    return downloader.download(url, **kwargs)


class MultiThreadDownloader:

    def __init__(self):
        # Initialize all necessary attributes to avoid AttributeError
        self.threads = []
        self.total_size = 0
        self.url = ""
        self.method='get'
        self.output_filename = ""
        self.output_dir = ""
        self.temp_dir = ""
        self.log_dir = ""
        self.progress_file = ""
        self.response_log_file = ""
        self.num_threads = 2
        self.buffer_size = 10 * 1024 * 1024
        self.chunk_size = 8192
        self.is_downloading = False
        self.start_time = 0
        self.last_update_time = 0
        self.last_downloaded = 0
        self.current_speed = 0
        self.average_speed = 0
        self.total_downloaded_this_session = 0

        # Initialize locks - these will be reinitialized in each process
        self.lock = None
        self.progress_lock = None
        self.response_lock = None
        self.print_lock = None

    def run(self, urls, **kwargs):
        """
        Run downloader with multiple processes

        Args:
            urls: List of URLs to download
            **kwargs: Additional parameters

        Returns:
            List of download results
        """
        # Determine number of processes
        if isinstance(urls, str):
            urls = [urls]
        num_process = kwargs.get('process', min(len(urls), 4))  # Default to min(url_count, 4)
        num_process = min(len(urls), num_process)

        print(f"Starting {num_process} processes for {len(urls)} URLs")

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

        # Prepare arguments for each URL with process index
        download_args = []
        for i, url in enumerate(urls):
            download_args.append((url, kwargs, i, progress_queue))



        # Create process pool
        with Pool(processes=num_process) as pool:
            results = pool.map(download_single_url, download_args)

        # Wait for monitor process to finish
        monitor_process.join(timeout=10)
        if monitor_process.is_alive():
            monitor_process.terminate()

        # Check for incomplete downloads and retry if needed
        successful_count = sum(results)
        if successful_count < len(results):
            print(f"\nSome downloads failed. {successful_count} successful out of {len(results)}")
            print("Attempting to resume failed downloads...")

            # Retry failed downloads (only for retryable errors)
            retry_args = []
            for i, (success, url) in enumerate(zip(results, urls)):
                if not success:
                    retry_args.append((url, kwargs, i, progress_queue))

            if retry_args:
                print(f"Retrying {len(retry_args)} failed downloads...")

                # Restart monitor for retry
                monitor_process = Process(
                    target=progress_monitor,
                    args=(progress_queue, len(retry_args), 1)
                )
                monitor_process.start()

                # Give monitor time to initialize
                time.sleep(0.5)

                with Pool(processes=min(len(retry_args), num_process)) as pool:
                    retry_results = pool.map(download_single_url, retry_args)

                # Update results
                retry_index = 0
                for i in range(len(results)):
                    if not results[i]:
                        results[i] = retry_results[retry_index]
                        retry_index += 1

                successful_count = sum(results)

                # Wait for monitor to finish
                monitor_process.join(timeout=10)
                if monitor_process.is_alive():
                    monitor_process.terminate()

                print(f"After retry: {successful_count} successful out of {len(results)}")

        print(f"\nAll downloads completed. Results: {successful_count} successful out of {len(results)}")
        return results

    def download(self, url, **kwargs):
        """
        Download single URL (for backward compatibility)

        Args:
            url: URL to download
            **kwargs: Additional parameters

        Returns:
            Download result
        """
        downloader = SingleURLDownloader(0, None)  # Default process index 0
        return downloader.download(url, **kwargs)


class SingleURLDownloader:
    """
    Downloader for single URL that can be used in multiprocessing
    """

    def __init__(self, process_index=0, progress_queue=None):
        # Initialize all necessary attributes
        self.threads = []
        self.total_size = 0
        self.url = ""
        self.output_filename = ""
        self.output_dir = ""
        self.temp_dir = ""
        self.log_dir = ""
        self.progress_file = ""
        self.response_log_file = ""
        self.num_threads = 2
        self.buffer_size = 10 * 1024 * 1024
        self.chunk_size = 8192
        self.is_downloading = False
        self.start_time = 0
        self.last_update_time = 0
        self.last_downloaded = 0
        self.current_speed = 0
        self.average_speed = 0
        self.total_downloaded_this_session = 0
        self.process_index = process_index  # Track which process this is
        self.max_retries = 3  # Default maximum number of retry attempts
        self.retry_count = 0  # Current retry count
        self.progress_queue = progress_queue  # Queue for progress updates

        # Buffer management
        self.max_memory_buffer = 100 * 1024 * 1024  # 100MB max memory buffer
        self.current_buffer_size = 0

        # Initialize locks in each process
        self.lock = threading.Lock()
        self.progress_lock = threading.Lock()
        self.response_lock = threading.Lock()
        self.print_lock = threading.Lock()

    def send_progress_update(self, progress_data):
        """
        Send progress update to monitor process
        """
        if self.progress_queue:
            try:
                progress_data['type'] = 'progress'
                progress_data['process_id'] = self.process_index
                progress_data['timestamp'] = time.time()
                self.progress_queue.put(progress_data)
            except:
                pass  # Ignore queue errors

    def send_completion_update(self, message):
        """
        Send completion update to monitor process
        """
        if self.progress_queue:
            try:
                self.progress_queue.put({
                    'type': 'complete',
                    'process_id': self.process_index,
                    'message': message,
                    'timestamp': time.time()
                })
            except:
                pass  # Ignore queue errors

    def is_retryable_error(self, error_msg, status_code=None):
        """
        Check if error is retryable based on status code or error type

        Args:
            error_msg: Error message string
            status_code: HTTP status code if available

        Returns:
            Boolean indicating if error is retryable
        """
        # Non-retryable status codes
        non_retryable_codes = [400, 401, 403, 404, 405, 410, 411, 412, 413, 414, 415, 416, 417, 422, 423, 424, 426, 428,
                               431, 451]

        if status_code is not None:
            # 5xx server errors and 429 (Too Many Requests) are retryable
            if status_code >= 500 or status_code == 429:
                return True
            # 4xx client errors (except 429) are generally non-retryable
            elif status_code >= 400 and status_code not in [429]:
                return False

        # Network-related errors are retryable
        network_errors = [
            'ConnectionError', 'ConnectTimeout', 'ReadTimeout', 'Timeout',
            'Connection refused', 'Name or service not known', 'DNS',
            'Network is unreachable', 'No route to host', 'Temporary failure in name resolution',
            'Max retries exceeded', 'Remote end closed connection'
        ]

        error_str = str(error_msg).lower()
        for network_error in network_errors:
            if network_error.lower() in error_str:
                return True

        # Default to non-retryable for unknown errors
        return False

    def download(self, url, **kwargs):
        """
        Main download method for single URL with automatic retry

        Args:
            url: URL to download
            **kwargs: Additional parameters

        Returns:
            Download result
        """
        # Get retry count from kwargs, default to 3
        self.max_retries = kwargs.get('retry_num', 3)
        self.method = kwargs.get('method', 'get').lower()
        self.retry_count = 0

        while self.retry_count <= self.max_retries:
            try:
                # Initialize downloader attributes
                self._init_downloader_attributes(url, kwargs)

                # Send initial progress update
                self.send_progress_update({
                    'url_short': url[:60] + "..." if len(url) > 60 else url,
                    'progress_percent': 0,
                    'downloaded_str': '0B',
                    'total_str': 'Unknown',
                    'speed_str': '0 B/s',
                    'eta_str': 'Unknown',
                    'status': 'starting',
                    'retry_count': self.retry_count,
                    'max_retries': self.max_retries
                })

                # Create directories
                self._create_directories()

                if self.retry_count > 0:
                    self.send_progress_update({
                        'status': f'retry_{self.retry_count}'
                    })

                # Check if previous download progress exists
                if os.path.exists(self.progress_file):
                    result = self.start_download(resume=True)
                else:
                    result = self.start_download(resume=False)

                if result:
                    filename = self.get_filename_from_url(url)
                    self.send_completion_update(f"Download completed: {filename}")
                    return True
                else:
                    # Download incomplete, check if we should retry
                    self.retry_count += 1
                    if self.retry_count <= self.max_retries:
                        wait_time = 2 * self.retry_count  # Exponential backoff
                        self.send_progress_update({
                            'status': f'waiting_retry_{self.retry_count}',
                            'wait_time': wait_time
                        })
                        time.sleep(wait_time)
                    else:
                        self.send_completion_update(f"Download failed after {self.max_retries} retries")
                        return False

            except Exception as e:
                # Check if error is retryable
                if self.is_retryable_error(str(e)):
                    self.retry_count += 1
                    if self.retry_count <= self.max_retries:
                        wait_time = 2 * self.retry_count  # Exponential backoff
                        self.send_progress_update({
                            'status': f'error_retryable_{self.retry_count}: {str(e)}',
                            'wait_time': wait_time
                        })
                        time.sleep(wait_time)
                    else:
                        self.send_completion_update(f"Download failed after {self.max_retries} retries: {str(e)}")
                        return False
                else:
                    # Non-retryable error
                    self.send_completion_update(f"Download failed (non-retryable): {str(e)}")
                    return False

        return False

    def _init_downloader_attributes(self, url, kwargs):
        """
        Initialize downloader attributes

        Args:
            url: URL to download
            kwargs: Additional parameters
        """
        self.url = url
        self.output_filename = kwargs.get('output_filename', self.get_filename_from_url(self.url))
        self.request_fingerprint = self.generate_fingerprint(self.url, kwargs)
        self.total_size = 0
        self.num_threads = kwargs.get('threads', 2)

        # Set output directories
        base_output_dir = kwargs.get('output_dir', 'output')
        self.output_dir = f"{base_output_dir}/{self.output_filename}"
        self.output_dir = self.output_dir.replace(".tar","")
        self.temp_dir = f"{self.output_dir}/tmp"
        self.log_dir = f"{self.output_dir}/log"

        # Set log files
        self.progress_file = f"{self.log_dir}/{kwargs.get('progress_file', 'download_progress.json')}"
        self.response_log_file = f"{self.log_dir}/{kwargs.get('response_log_file', 'response_state.log')}"

        # Set buffer and chunk sizes
        self.buffer_size = kwargs.get('buffer_size_mb', 10) * 1024 * 1024  # 10MB
        self.chunk_size = kwargs.get('chunk_size', 8192)  # 8KB

        # Initialize threads list
        self.threads = []

        # Download control
        self.is_downloading = False
        self.last_progress_save = 0
        self.progress_save_interval = 5  # Save progress every 5 seconds
        self.last_progress_update = 0
        self.progress_update_interval = 1  # Update progress every 1 second

        # Request parameters
        self.headers = kwargs.get('headers', self.get_header())
        self.params = kwargs.get('params')
        self.data = kwargs.get('data')
        self.json = kwargs.get('json')
        self.proxies = kwargs.get('proxies')
        self.cookies = kwargs.get('cookies')
        self.auth = kwargs.get('auth')
        self.verify = kwargs.get('verify', False)
        self.cert = kwargs.get('cert')
        self.timeout = kwargs.get('timeout', 30)
        self.allow_redirects = kwargs.get('allow_redirects', True)
        self.stream = kwargs.get('stream', True)
        self.max_retries = kwargs.get('retry_num', 3)
        self.method = kwargs.get('method', 'get')


        # Download statistics
        self.start_time = 0
        self.last_update_time = 0
        self.last_downloaded = 0
        self.current_speed = 0
        self.average_speed = 0
        self.total_downloaded_this_session = 0

    def _create_directories(self):
        """Create necessary directories"""
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def generate_fingerprint(self, url=None, kwargs=None):
        """
        Generate fingerprint for request

        Args:
            url: URL
            kwargs: Additional parameters

        Returns:
            MD5 fingerprint string
        """
        # Sort parameters and convert to JSON for consistency
        sorted_kwargs = json.dumps(kwargs, sort_keys=True) if kwargs else "{}"
        data = f"{url}{sorted_kwargs}"

        # Generate MD5 fingerprint
        fingerprint = hashlib.md5(data.encode('utf-8')).hexdigest()
        return fingerprint

    def get_header(self):
        """
        Get default headers

        Returns:
            Dictionary of default headers
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'identity',
            'Connection': 'keep-alive'
        }
        return headers

    def _prepare_request_kwargs(self):
        """
        Prepare request parameters

        Returns:
            Dictionary of request parameters
        """
        request_kwargs = {
            'headers': self.headers,
            'params': self.params,
            'data': self.data,
            'json': self.json,
            'proxies': self.proxies,
            'cookies': self.cookies,
            'auth': self.auth,
            'verify': self.verify,
            'cert': self.cert,
            'timeout': self.timeout,
            'allow_redirects': self.allow_redirects,
            'stream': self.stream
        }
        # Clean empty parameters
        return {k: v for k, v in request_kwargs.items() if v is not None}

    def get_file_size(self) -> int:
        """
        Get actual file size from URL

        Returns:
            File size in bytes, 0 if cannot determine
        """
        try:
            # Use HEAD request to get file size without downloading content
            request_kwargs = self._prepare_request_kwargs()
            # Use HEAD method instead of GET to avoid downloading content
            response = requests.head(self.url, **request_kwargs)
            # Check for non-retryable status codes
            if response.status_code in [404, 403, 410]:
                raise Exception(f"Non-retryable error: HTTP {response.status_code} - File not found or access denied")

            # If HEAD not allowed, try GET with Range header
            if response.status_code == 405 or 'Content-Length' not in response.headers:
                headers = request_kwargs.get('headers', {}).copy()
                headers['Range'] = 'bytes=0-0'
                request_kwargs['headers'] = headers

                if self.method == 'post':
                    response = requests.post(self.url, **request_kwargs)
                else:
                    response = requests.get(self.url, **request_kwargs)


                # Check for non-retryable status codes in GET request
                if response.status_code in [404, 403, 410]:
                    raise Exception(
                        f"Non-retryable error: HTTP {response.status_code} - File not found or access denied")

            if response.status_code in [200, 206]:
                if 'Content-Length' in response.headers:
                    size = int(response.headers['Content-Length'])
                    return size
                elif 'Content-Range' in response.headers:
                    content_range = response.headers['Content-Range']
                    size = int(content_range.split('/')[-1])
                    return size
                else:
                    return 0
            else:
                # For other status codes, decide whether to retry
                if self.is_retryable_error(f"HTTP {response.status_code}", response.status_code):
                    # Retryable server errors
                    raise Exception(f"Retryable error: HTTP {response.status_code}")
                else:
                    # Other client errors - non-retryable
                    raise Exception(f"Non-retryable error: HTTP {response.status_code}")

        except requests.exceptions.RequestException as e:
            # Network-related errors (DNS, connection, timeout, etc.)
            if self.is_retryable_error(str(e)):
                raise Exception(f"Retryable network error: {str(e)}")
            else:
                raise Exception(f"Non-retryable network error: {str(e)}")
        except Exception as e:
            # Re-raise the exception to handle in calling code
            raise e

    def calculate_ranges(self) -> List[Dict]:
        """
        Calculate download ranges for each thread

        Returns:
            List of thread range information dictionaries
        """
        ranges = []

        if self.total_size <= 0:
            # If cannot get file size, use single thread download
            temp_file = os.path.join(self.temp_dir, "part_0.tmp")
            ranges.append({
                "thread_id": 0,
                "start": 0,
                "end": None,  # No end position
                "downloaded": 0,
                "current_pos": 0,
                "temp_file": temp_file,
                "status": "pending",
                "last_save_time": 0
            })
        else:
            chunk_size = self.total_size // self.num_threads

            for i in range(self.num_threads):
                start = i * chunk_size
                # Last thread downloads all remaining content
                if i == self.num_threads - 1:
                    end = self.total_size - 1
                else:
                    end = start + chunk_size - 1

                temp_file = os.path.join(self.temp_dir, f"part_{i}.tmp")

                # Check if temp file exists, get downloaded size if exists
                downloaded = 0
                current_pos = start
                file_exists = os.path.exists(temp_file)

                if file_exists:
                    try:
                        downloaded = os.path.getsize(temp_file)
                        current_pos = start + downloaded
                    except OSError as e:
                        # File might be corrupted, re-download
                        try:
                            os.remove(temp_file)
                        except:
                            pass
                        downloaded = 0
                        current_pos = start

                ranges.append({
                    "thread_id": i,
                    "start": start,
                    "end": end,
                    "downloaded": downloaded,
                    "current_pos": current_pos,
                    "temp_file": temp_file,
                    "status": "pending",
                    "last_save_time": 0
                })

        return ranges

    def download_chunk(self, thread_info: Dict):
        """
        Download file chunk

        Args:
            thread_info: Thread information dictionary
        """
        thread_id = thread_info["thread_id"]

        # Skip if already completed
        if thread_info["end"] is not None and thread_info["current_pos"] > thread_info["end"]:
            thread_info["status"] = "completed"
            return

        request_kwargs = self._prepare_request_kwargs()
        headers = request_kwargs.get('headers', {}).copy()

        # Add Range header (if file size is known)
        if thread_info["end"] is not None:
            headers['Range'] = f'bytes={thread_info["current_pos"]}-{thread_info["end"]}'
        else:
            # When file size is unknown, download from current position
            if thread_info["current_pos"] > 0:
                headers['Range'] = f'bytes={thread_info["current_pos"]}-'

        try:
            thread_info["status"] = "downloading"
            # Create session with retry
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=3)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            request_kwargs['headers'] = headers

            if self.method=='post':
                 response = session.post(self.url, **request_kwargs)
            else:
                response = session.get(self.url, **request_kwargs)
            response.raise_for_status()

            # Check response status for non-retryable errors
            if response.status_code in [404, 403, 410]:
                raise Exception(f"Non-retryable error: HTTP {response.status_code} - File not found or access denied")

            # Check for other errors
            if response.status_code not in [200, 206]:
                if self.is_retryable_error(f"HTTP {response.status_code}", response.status_code):
                    # Server errors - retryable
                    raise Exception(f"Retryable error: HTTP {response.status_code}")
                else:
                    # Other client errors - non-retryable
                    raise Exception(f"Non-retryable error: HTTP {response.status_code}")

            # Open file for writing
            mode = 'ab' if os.path.exists(thread_info["temp_file"]) else 'wb'
            with open(thread_info["temp_file"], mode) as f:
                buffer = b""
                buffer_size = 0
                last_save_time = time.time()

                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    if not self.is_downloading:
                        break

                    if chunk:
                        buffer += chunk
                        buffer_size += len(chunk)

                        # Check if buffer exceeds memory limit
                        if buffer_size >= self.max_memory_buffer:
                            # Write to disk to prevent memory overflow
                            f.write(buffer)
                            f.flush()
                            os.fsync(f.fileno())

                            with self.lock:
                                thread_info["downloaded"] += buffer_size
                                thread_info["current_pos"] += buffer_size
                                self.total_downloaded_this_session += buffer_size

                            # Reset buffer
                            buffer = b""
                            buffer_size = 0
                            last_save_time = time.time()

                        # Check if buffer reaches specified size or needs flushing
                        current_time = time.time()
                        if buffer_size >= self.chunk_size or current_time - last_save_time >= 2:
                            f.write(buffer)
                            f.flush()
                            os.fsync(f.fileno())  # Ensure data written to disk

                            with self.lock:
                                thread_info["downloaded"] += buffer_size
                                thread_info["current_pos"] += buffer_size
                                self.total_downloaded_this_session += buffer_size

                            # Reset buffer
                            buffer = b""
                            buffer_size = 0
                            last_save_time = current_time

                            # Check if need to save progress
                            if current_time - thread_info["last_save_time"] >= 2:
                                thread_info["last_save_time"] = current_time
                                # Use separate thread to save progress to avoid blocking download
                                threading.Thread(target=self.save_progress, daemon=True).start()

                # Write remaining buffer data
                if buffer_size > 0 and self.is_downloading:
                    f.write(buffer)
                    f.flush()
                    os.fsync(f.fileno())

                    with self.lock:
                        thread_info["downloaded"] += buffer_size
                        thread_info["current_pos"] += buffer_size
                        self.total_downloaded_this_session += buffer_size

            if self.is_downloading:
                thread_info["status"] = "completed"
            else:
                thread_info["status"] = "paused"

        except Exception as e:
            with self.print_lock:
                thread_info["status"] = "error"
            # Re-raise to handle in calling code
            raise e

    def save_progress(self):
        """
        Save download progress to JSON file - thread safe with lock
        """
        if not hasattr(self, 'threads') or not self.threads:
            return

        # Use progress lock to ensure only one thread saves progress at a time
        if not self.progress_lock.acquire(blocking=False):
            # Skip if lock is already acquired
            return

        try:
            # Check if need to save (avoid too frequent)
            current_time = time.time()
            if current_time - self.last_progress_save < 1:  # Save at least every 1 second
                return

            progress_data = {
                "url": self.url,
                "total_size": self.total_size,
                "num_threads": self.num_threads,
                "temp_dir": self.temp_dir,
                "buffer_size": self.buffer_size,
                "threads": self.threads,
                "timestamp": current_time,
                "save_time": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            # Use temp file for atomic write
            temp_file = self.progress_file + ".tmp"
            directory = os.path.dirname(temp_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            # Try to write temp file
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(progress_data, f, indent=2, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())
            except Exception as e:
                return

            # Try to rename file
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Delete target file if exists
                    if os.path.exists(self.progress_file):
                        os.remove(self.progress_file)

                    # Rename temp file
                    os.rename(temp_file, self.progress_file)
                    self.last_progress_save = current_time
                    break  # Success, exit retry loop

                except (OSError, IOError) as e:
                    if attempt < max_retries - 1:
                        # Wait and retry
                        time.sleep(0.1)
                    else:
                        # Clean up temp file
                        try:
                            if os.path.exists(temp_file):
                                os.remove(temp_file)
                        except:
                            pass

        finally:
            # Ensure lock is released
            self.progress_lock.release()

    def load_progress(self) -> bool:
        """
        Load download progress from JSON file

        Returns:
            True if progress loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(self.progress_file):
                return False

            with open(self.progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate data integrity
            required_keys = ["url", "total_size", "num_threads", "threads"]
            if not all(key in data for key in required_keys):
                return False

            # Restore data
            self.url = data["url"]
            self.total_size = data["total_size"]
            self.num_threads = data["num_threads"]

            if "temp_dir" in data:
                self.temp_dir = data["temp_dir"]

            if "buffer_size" in data:
                self.buffer_size = data["buffer_size"]

            # Validate and restore thread data
            recovered_threads = []
            for thread_data in data["threads"]:
                temp_file = thread_data["temp_file"]
                expected_downloaded = thread_data["downloaded"]

                # Validate temp file
                if os.path.exists(temp_file):
                    actual_size = os.path.getsize(temp_file)

                    if actual_size == expected_downloaded:
                        # File size matches
                        thread_data["last_save_time"] = 0
                        recovered_threads.append(thread_data)
                    else:
                        # File size mismatch, use actual size
                        thread_data["downloaded"] = actual_size
                        thread_data["current_pos"] = thread_data["start"] + actual_size
                        thread_data["status"] = "pending"
                        thread_data["last_save_time"] = 0
                        recovered_threads.append(thread_data)
                else:
                    # Temp file doesn't exist
                    thread_data["downloaded"] = 0
                    thread_data["current_pos"] = thread_data["start"]
                    thread_data["status"] = "pending"
                    thread_data["last_save_time"] = 0
                    recovered_threads.append(thread_data)

            self.threads = recovered_threads
            return True

        except Exception as e:
            return False

    def get_download_info(self):
        """
        Get download statistics information

        Returns:
            Dictionary with download info
        """
        # Check if threads attribute exists
        if not hasattr(self, 'threads') or not self.threads:
            return {
                "total_downloaded": 0,
                "total_size": self.total_size if hasattr(self, 'total_size') else 0,
                "progress_percent": 0,
                "completed_threads": 0,
                "active_threads": 0,
                "total_threads": 0
            }

        total_downloaded = sum(thread["downloaded"] for thread in self.threads)
        completed_threads = sum(1 for thread in self.threads if thread["status"] == "completed")
        active_threads = sum(1 for thread in self.threads if thread["status"] == "downloading")

        progress_percent = 0
        if self.total_size > 0:
            progress_percent = (total_downloaded / self.total_size) * 100

        return {
            "total_downloaded": total_downloaded,
            "total_size": self.total_size,
            "progress_percent": progress_percent,
            "completed_threads": completed_threads,
            "active_threads": active_threads,
            "total_threads": len(self.threads)
        }

    def update_speed_stats(self, current_downloaded: int, current_time: float):
        """
        Update download speed statistics

        Args:
            current_downloaded: Current downloaded bytes
            current_time: Current timestamp
        """
        if self.last_update_time == 0:
            # First update
            self.last_update_time = current_time
            self.last_downloaded = current_downloaded
            return

        time_diff = current_time - self.last_update_time
        if time_diff >= 1.0:  # Update speed at least every 1 second
            downloaded_diff = current_downloaded - self.last_downloaded
            self.current_speed = downloaded_diff / time_diff  # bytes/second

            # Update average speed
            if self.start_time > 0:
                elapsed_time = current_time - self.start_time
                if elapsed_time > 0:
                    self.average_speed = current_downloaded / elapsed_time

            self.last_update_time = current_time
            self.last_downloaded = current_downloaded

    def format_speed(self, speed_bytes: float) -> str:
        """
        Format speed display

        Args:
            speed_bytes: Speed in bytes/second

        Returns:
            Formatted speed string
        """
        if speed_bytes <= 0:
            return "0 B/s"

        if speed_bytes < 1024:
            return f"{speed_bytes:.0f} B/s"
        elif speed_bytes < 1024 * 1024:
            return f"{speed_bytes / 1024:.1f} KB/s"
        else:
            return f"{speed_bytes / (1024 * 1024):.1f} MB/s"

    def format_eta(self, remaining_bytes: int, speed: float) -> str:
        """
        Calculate and format estimated remaining time

        Args:
            remaining_bytes: Remaining bytes to download
            speed: Download speed in bytes/second

        Returns:
            Formatted ETA string
        """
        if speed <= 0 or remaining_bytes <= 0:
            return "Unknown"

        seconds = remaining_bytes / speed
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds / 60)}m{int(seconds % 60)}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h{minutes}m"

    def format_size_smart(self, size_bytes):
        """
        Smart format file size

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)

        # Automatically select appropriate unit
        if i >= 3:  # GB or TB
            return f"{s:.1f}G"
        elif i == 2:  # MB
            if size_bytes >= 500 * 1024 * 1024:  # Larger than 500MB show as G
                return f"{size_bytes / 1024 / 1024 / 1024:.1f}G"
            return f"{s:.0f}MB"
        elif i == 1:  # KB
            return f"{s:.0f}KB"
        else:  # B
            return f"{s:.0f}B"

    def start_download(self, resume: bool = False):
        """
        Start download

        Args:
            resume: Whether to resume previous download

        Returns:
            True if download successful, False otherwise
        """
        # Set output file path
        if not self.output_filename:
            output_file = f"{self.temp_dir}{self.get_filename_from_url(self.url)}"
        else:
            output_file = f"{self.output_dir}/{self.output_filename}"

        try:
            # Get file size (for new download)
            if not resume or not os.path.exists(self.progress_file):
                try:
                    self.total_size = self.get_file_size()
                    if self.total_size <= 0:
                        pass  # Don't print in monitor mode
                except Exception as e:
                    # Check if it's a non-retryable error
                    if "Non-retryable" in str(e):
                        self.send_progress_update({
                            'status': f'non_retryable_error: {str(e)}'
                        })
                        self.send_completion_update(f"Download failed: {str(e)}")
                        return False
                    else:
                        # Retryable error, continue
                        pass

            self.is_downloading = True
            self.start_time = time.time()
            self.last_update_time = 0
            self.last_downloaded = 0
            self.current_speed = 0
            self.average_speed = 0
            self.total_downloaded_this_session = 0

            # Load or initialize progress
            if resume and self.load_progress():
                pass
            else:
                self.threads = self.calculate_ranges()
                self.save_progress()  # Save initial progress immediately

            # Start download threads
            download_threads = []
            for thread_info in self.threads:
                if thread_info["status"] != "completed":
                    thread = threading.Thread(
                        target=self.download_chunk,
                        args=(thread_info,),
                        daemon=True
                    )
                    download_threads.append(thread)
                    thread.start()

            # Monitor progress
            return self.monitor_progress(download_threads, output_file)

        except Exception as e:
            self.is_downloading = False
            # Check if it's a non-retryable error
            if "Non-retryable" in str(e):
                self.send_completion_update(f"Download failed: {str(e)}")
                return False
            else:
                # Retryable error, return False to trigger retry
                return False

    def monitor_progress(self, download_threads: List[threading.Thread], output_file: str):
        """
        Monitor download progress

        Args:
            download_threads: List of download threads
            output_file: Output file path

        Returns:
            True if download successful, False otherwise
        """
        try:
            last_save_time = time.time()

            while any(thread.is_alive() for thread in download_threads) and self.is_downloading:
                current_time = time.time()

                # Get current download info
                info = self.get_download_info()

                # Update speed statistics
                self.update_speed_stats(info['total_downloaded'], current_time)

                # Periodically save progress (controlled by main thread)
                if current_time - last_save_time >= self.progress_save_interval:
                    threading.Thread(target=self.save_progress, daemon=True).start()
                    last_save_time = current_time

                # Periodically send progress update
                if current_time - self.last_progress_update >= self.progress_update_interval:
                    downloaded_str = self.format_size_smart(info['total_downloaded'])
                    total_str = self.format_size_smart(self.total_size) if self.total_size > 0 else "Unknown"

                    progress_percent = 0
                    if self.total_size > 0:
                        progress_percent = info['progress_percent']
                    else:
                        progress_percent = 0

                    # Calculate ETA
                    if self.total_size > 0 and self.average_speed > 0:
                        remaining_bytes = self.total_size - info['total_downloaded']
                        eta_str = self.format_eta(remaining_bytes, self.average_speed)
                    else:
                        eta_str = "Unknown"

                    # Format speed display
                    speed_str = self.format_speed(self.current_speed)

                    # Send progress update
                    self.send_progress_update({
                        'url_short': self.url[:60] + "..." if len(self.url) > 60 else self.url,
                        'progress_percent': progress_percent,
                        'downloaded_str': downloaded_str,
                        'total_str': total_str,
                        'speed_str': speed_str,
                        'eta_str': eta_str,
                        'status': 'downloading',
                        'retry_count': self.retry_count,
                        'max_retries': self.max_retries
                    })

                    self.last_progress_update = current_time

                time.sleep(0.1)

            # Wait for all threads to complete
            for thread in download_threads:
                thread.join(timeout=5)

            # All threads completed or download stopped
            if self.is_downloading:
                # Check if all threads completed
                info = self.get_download_info()
                if info['completed_threads'] == info['total_threads']:
                    self.merge_files(output_file)
                    self.cleanup()
                    return True
                else:
                    # Save progress for resume
                    self.save_progress()
                    return False
            else:
                # Save progress for resume
                self.save_progress()
                return False

        except KeyboardInterrupt:
            self.is_downloading = False
            # Save progress for resume
            self.save_progress()
            return False
        except Exception as e:
            self.is_downloading = False
            # Save progress for resume
            self.save_progress()
            return False

    def merge_files(self, output_file: str):
        """
        Merge temporary files

        Args:
            output_file: Output file path
        """
        try:
            with open(output_file, 'wb') as outfile:
                for thread_info in sorted(self.threads, key=lambda x: x["thread_id"]):
                    temp_file = thread_info["temp_file"]
                    if os.path.exists(temp_file):
                        with open(temp_file, 'rb') as infile:
                            while True:
                                chunk = infile.read(self.chunk_size)
                                if not chunk:
                                    break
                                outfile.write(chunk)
        except Exception as e:
            pass

    def cleanup(self):
        """Clean up temporary files and progress files"""
        try:
            # Clean temp files
            for thread_info in self.threads:
                temp_file = thread_info["temp_file"]
                if os.path.exists(temp_file):
                    os.remove(temp_file)

            # Clean progress file
            if os.path.exists(self.progress_file):
                os.remove(self.progress_file)

            try:
                if os.path.exists(self.log_dir) and os.path.isdir(self.log_dir):
                    shutil.rmtree(self.log_dir)
            except:
                pass

            try:
                if os.path.exists(self.temp_dir) and os.path.isdir(self.temp_dir):
                    shutil.rmtree(self.temp_dir)
            except:
                pass

        except:
            pass

    def get_filename_from_url(self, url: str) -> str:
        """
        Extract filename from URL

        Args:
            url: URL string

        Returns:
            Filename or None if cannot extract
        """
        try:
            parsed_url = urllib.parse.urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename:
                # If no filename in path, try to get from query parameters
                query_params = urllib.parse.parse_qs(parsed_url.query)
                for key in ['filename', 'file', 'name']:
                    if key in query_params:
                        filename = query_params[key][0]
                        break
            return filename if filename and '.' in filename else "download_file"
        except:
            return "download_file"


def main():
    """Main function for testing"""
    download_urls=[]
    for i in range(1, 10):
        url = f'https://huggingface.co/datasets/UCSC-VLAA/Recap-DataComp-1B/resolve/main/data/train_data/train-0000{i}-of-04627.parquet'
        download_urls.append(url)

    download_urls='https://huggingface.co/datasets/UCSC-VLAA/Recap-DataComp-1B/resolve/main/data/train_data/train-00001-of-04627.parquet'
    downloader = MultiThreadDownloader()
    results = downloader.run(
        urls=download_urls,
        process=4,  # Use 4 processes for 4 URLs
        threads=10
    )

    print(f"All downloads completed. Results: {sum(results)} successful out of {len(results)}")


if __name__ == "__main__":
    main()


