Multi-Process Multi-Thread Downloader
A high-performance, robust download manager built with Python that supports both multi-process and multi-thread downloading with intelligent error handling and resume capabilities.
MarsCore (Mars Core) - Developed by Chinese developer Mars (formerly: Ma Yu Chao)，A high-performance, robust download manager built with Python that supports both multi-process，and multi-thread downloading with intelligent error handling and resume capabilities.

🚀 Features
Multi-Process Architecture: Download multiple files simultaneously using separate processes

Multi-Thread Downloading: Split large files into chunks and download concurrently

Intelligent Error Handling: Smart retry mechanism for different types of errors

Resume Support: Continue interrupted downloads from where they left off

Progress Monitoring: Real-time progress tracking with speed and ETA

Memory Management: Configurable buffer sizes to prevent memory overflow

Configurable Retry Logic: Customizable retry counts for different error types

📋 Requirements
bash
pip install marscore

import marscore

urls = [
    "https://example.com/file1.zip",
    "https://example.com/file2.zip",
    "https://example.com/file3.zip"
]

 results = marscore.downloader(
        urls=download_urls,
        process=4,  # Use 4 processes for 4 URLs
        threads=10
    )

print(f"All downloads completed. Results: {sum(results)} successful out of {len(results)}")


⚙️ Configuration Parameters
Download Parameters
url: Target URL to download

output_dir: Output directory (default: 'output')

output_filename: Custom filename for the downloaded file

threads: Number of threads per download (default: 2)

process: Number of processes for multiple downloads (default: min(url_count, 4))

Performance Parameters
buffer_size_mb: Memory buffer size in MB (default: 10)

chunk_size: Download chunk size in bytes (default: 8192)

retry_num: Maximum retry attempts (default: 3)

Network Parameters
headers: Custom HTTP headers

timeout: Request timeout in seconds (default: 30)

proxies: Proxy configuration

verify: SSL verification (default: False)

🔧 Advanced Configuration
Custom Headers
python
custom_headers = {
    'User-Agent': 'Custom User Agent',
    'Authorization': 'Bearer token'
}

marscore.downloader(
    url="https://example.com/file.zip",
    headers=custom_headers,
    threads=8
)

With Proxy
python
proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'https://proxy.example.com:8080'
}

marscore.downloader(
    url="https://example.com/file.zip",
    proxies=proxies,
    threads=4
)



🎯 Error Handling
Retryable Errors (will retry based on retry_num)
HTTP Status Codes: 500, 502, 503, 504, 429

Network Errors: Connection timeouts, DNS resolution failures, network interruptions

Temporary Issues: Server overload, rate limiting

Non-Retryable Errors (immediate failure)
HTTP Status Codes: 404, 403, 410

Client Errors: File not found, access denied, authentication issues

Custom Retry Configuration
python
# Retry up to 10 times for server errors
marscore.downloader(
    urls=urls,
    retry_num=10,
    threads=4
)


📊 Progress Monitoring
The downloader provides real-time progress information including:

Download percentage

Download speed (B/s, KB/s, MB/s)

Estimated time remaining (ETA)

Active vs completed threads

Retry attempts and status

💾 Memory Management
To prevent memory overflow during large concurrent downloads:

Automatic buffer flushing: Data is written to disk when buffer reaches configured size

Configurable memory limits: Set maximum memory usage with buffer_size_mb

Efficient chunking: Downloads are split into manageable chunks

python
# Conservative memory usage
marscore.downloader(
    url="https://example.com/very-large-file.iso",
    buffer_size_mb=5,    # 5MB buffer
    chunk_size=4096,     # 4KB chunks
    threads=4
)

🏗️ Architecture
Multi-Process Level
Each URL is processed in a separate process

Independent progress monitoring for each download

Process pool for efficient resource utilization

Multi-Thread Level
Each file is split into multiple chunks

Concurrent downloading of chunks using threads

Thread-safe progress tracking and file writing

Progress Communication
Manager Queue for inter-process communication

Real-time progress updates to monitor process

Thread-safe locking mechanisms

🔄 Resume Capability
The downloader automatically:

Saves progress at regular intervals

Resumes from the last saved position after interruptions

Validates downloaded chunks for integrity

Cleans up temporary files after successful completion



🚨 Error Recovery
The downloader handles various failure scenarios:

Network Interruptions: Automatically resumes when connection is restored

Server Errors: Retries with exponential backoff

Disk Space Issues: Clean error reporting and graceful shutdown

Permission Problems: Clear error messages for file access issues

📈 Performance Tips
Optimal Thread Count: 4-8 threads per download usually provides best performance

Memory Configuration: Adjust buffer size based on available RAM

Network Settings: Increase timeout for slow connections

Process Count: Match process count to CPU cores for optimal performance

👨‍💻 Author
marscore (原名: Ma Yu Chao)

Email: marscore@163.com

GitHub: https://github.com/mars-core/

📄 License
This project is open source and available under the MIT License.

🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

⚠️ Disclaimer
Use this downloader responsibly and in compliance with:

Website terms of service

Copyright laws

Rate limiting policies

Server resource constraints