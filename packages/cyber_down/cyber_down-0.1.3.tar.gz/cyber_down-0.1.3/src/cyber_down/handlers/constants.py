import os

# DOWNLOAD CONSTANTS
CHUNK_SIZE = 1024 * 1024  # 1MB chunks for download
MIN_CHUNK_DOWNLOAD_SIZE = 10 * 1024 * 1024  # 10MB minimum for chunked download

# THREADS
THREAD_COUNT = os.cpu_count()
THREADS = min(8, THREAD_COUNT if THREAD_COUNT else 4)  # Number of parallel chunks per file
MAX_CONCURRENT_DOWNLOADS = 2  # Number of files downloading simultaneously

TIMEOUT = 30  # Request timeout in seconds
