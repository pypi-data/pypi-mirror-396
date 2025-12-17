import os
import logging
import time

import requests

from pathlib import Path
from alive_progress import alive_bar
from typing import Tuple, List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from cyber_down.handlers.configs import logging_config
from cyber_down.handlers.download_metrics import _download_speed
from cyber_down.handlers.decorators import resume_streaming_download
from cyber_down.handlers.process_chunks import _download_multiple_chunks, _check_download_capability
from cyber_down.resolver.single_file_resolver import resolve_single_file_path, resolve_batch_file_path
from cyber_down.handlers.constants import (
    CHUNK_SIZE, MIN_CHUNK_DOWNLOAD_SIZE, MAX_CONCURRENT_DOWNLOADS, THREADS, TIMEOUT)

# CONFIGURE LOGGING
logger = logging_config(__name__, level=logging.DEBUG)


# Download a file
@resume_streaming_download
def _streaming_download(
        filename: str, link: str, filepath: str, temp_path: Optional[Path] = None,
        resume_mode: bool = False,  already_downloaded: int = 0,
        master_progress_bar: bool =False) -> Tuple[str, str, int]:
    """
    Standard download function with resume support

    :param filename: Name of file to download
    :param link: File source link
    :param filepath: Path to actual file in download directory
    :param resume_mode: Whether resuming a partial download
    :param temp_path: Path to temporary .part file
    :param already_downloaded: Bytes already downloaded
    :param master_progress_bar: If true, progress bar will not be displayed
    :return: (filepath, error_message, file size)
    """

    # Standard streaming download
    logger.debug(f"Using standard download for {filename}")

    try:
        # Setup headers
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36"
            ),
            "Accept": "*/*",
            "Accept-Encoding": "identity",
            "Connection": "keep-alive"
        }

        if resume_mode and already_downloaded > 0:
            headers['Range'] = f'bytes={already_downloaded}-'

        with requests.get(url=link, stream=True, timeout=TIMEOUT, headers=headers, allow_redirects=True) as response:

            # Check if resume is supported
            if resume_mode and response.status_code == 206:
                logger.info(f"Server supports resume, continuing from byte {already_downloaded}")

            elif resume_mode and response.status_code == 200:
                logger.warning(f"Server doesn't support resume, restarting download")

                if temp_path and temp_path.exists():
                    temp_path.unlink()

            else:
                response.raise_for_status()

            # Get total content length
            content_length = int(response.headers.get("content-length", 0))

            # Calculate total size (including already downloaded if resuming)
            if resume_mode and content_length > 0:
                file_size = already_downloaded + content_length

            else:
                file_size = content_length

            # Ensure parent directory exists
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            # Use temp file for downloading
            if not temp_path:
                temp_path = Path(filepath).parent / f"{Path(filepath).name}.part"

            # Open file in appropriate mode
            file_mode = 'ab' if resume_mode else 'wb'

            with temp_path.open(file_mode) as temp_file:

                if file_size == 0:
                        logger.warning(f"Downloading {filepath} with unknown file size")
                        temp_file.write(response.content)

                else:
                    current_bytes = already_downloaded if resume_mode else 0 # Tracked

                    start_time = time.time() # Track start time to calculate download speed


                if not master_progress_bar:
                        with alive_bar(
                            title= f"⬇ {filename}", total= file_size, spinner="pulse", bar="smooth",
                            monitor= '[{count}B / {total}B] {percent}%',stats= '[{rate}] [ETA: {eta}]'

                        ) as progress_bar:

                            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                                if chunk:
                                    temp_file.write(chunk)

                                    current_bytes += len(chunk) # added to the progress bar as a fraction
                                    _download_speed(downloaded=current_bytes, time_started=start_time, bar=progress_bar)

                                    progress_bar(current_bytes)

                # Don't display project bar if inside the main progress bar (yet...)
                else:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            temp_file.write(chunk)

                            current_bytes += len(chunk)  # added to the progress bar as a fraction

            # Move temp file to final location
            temp_path.rename(filepath)
            logger.info(f"Downloaded (standard): {filepath}")

            return filepath, "", file_size

    except Exception as e:
        logger.error(f"Streaming download failed for {filename}: {e}")

        # Keep temp file for potential resume
        logger.info(f"Temp file preserved for resume: {temp_path}")

        return "", f"Streaming download failed: {str(e)}", 0


# Break a file into chunks for faster download
def _parallel_segmented_download(
        filename: str, file_size: int, link: str, filepath: str,
        master_progress_bar: bool =False) -> Tuple[str, str, int]:
    """
    Parallel segmented download with IDM-style multi-chunk progress display

    :param filename: Name of file to download
    :param file_size: Total file size for chunk calculation
    :param link: File source link
    :param filepath: Path to actual file in download directory
    :param master_progress_bar: If true, progress bar will not be displayed
    :return: (filepath, error_message, file size)
    """

    # Chunked parallel download
    logger.debug(f"Using chunked download for {filename} ({file_size / 1024 / 1024:.2f} MB)")
    logger.info(f"Splitting into {THREADS} parallel chunks")


    success = _download_multiple_chunks(
        url=link, filepath=filepath, file_size=file_size, num_threads=THREADS,
        master_progress_bar=master_progress_bar)

    if success:
        logger.info(f"Downloaded (chunked): {filepath}")

        return filepath, "", file_size

    else:
        # Cleanup failed download
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.debug(f"Cleaned up failed download: {filepath}")

        return "", f"Chunked download failed for {filename}", 0


# Use single or multi-chunk downloading
def single_download(args: Tuple[str, Tuple[str, str],Optional[str], bool]) -> Tuple[str, str, int]:
    """
    Download an individual file using streaming or parallel segmented method

    :param args: (ext, (filename, link), folder name, master_progress_bar)
    :return: (filepath, error_message , file size) - one will be empty string, and file size
    """

    ext, file_data, folder_name, master_bar = args
    filename, link = file_data

    # Resolve filepath based on whether it's a batch or single download
    if folder_name:
        filepath = resolve_batch_file_path(folder_name, filename, ext)

    else:
        filepath = resolve_single_file_path(filename, ext)

    # Check if file already exists
    if os.path.exists(filepath):
        logger.info(f"File already exists: {filepath}")

        return filepath, "", 0

    # Use streaming or ps download
    try:
        # Check download capability
        is_accessible, file_size, supports_range = _check_download_capability(link)

        if not is_accessible:
            return "", f"Cannot access {filename}", 0

        if file_size == 0:
            logger.warning(f"Unknown file size for {filename}, using basic download")

        # Determine download type (True if it can use chunked downloading)
        use_chunked = ( supports_range and file_size > MIN_CHUNK_DOWNLOAD_SIZE and file_size > 0)

        # Parallel segmented downloading
        if use_chunked:
            download_metadata = _parallel_segmented_download(
                filename=filename,file_size= file_size,link= link,
                filepath= filepath,master_progress_bar=master_bar)

        # Streamline downloading
        else:
            download_metadata = _streaming_download(
                filename=filename, link=link, filepath=filepath, master_progress_bar=master_bar)

        return download_metadata

    except Exception as e:
        logger.error(f"Error downloading {filename}: {e}", exc_info=True)

        # Only cleanup if it's not a resumable download
        # For streaming downloads, temp files are preserved by _streaming_download
        # For chunked downloads, cleanup happens in _download_multiple_chunks
        if os.path.exists(filepath):
            os.remove(filepath)

        return "", f"{filename} failed: {str(e)}" , 0


# Cyber_Down a group of files
def batch_download(ext: str, folder_name: str, batch_urls: Dict[str, str]) -> List[str]:
    """
    Download a batch of files to a specific folder with progress tracking

    :param ext: File extension
    :param folder_name: Name of folder for batch downloads
    :param batch_urls: Dictionary of {filename: url}
    :return: List of successfully downloaded filepaths
    """

    logger.info(f"Downloading {len(batch_urls)} files to folder: {folder_name}")
    downloaded, failed = [], []

    # Prepare download arguments with folder name
    download_args = [(ext, file_data, folder_name , True) for file_data in batch_urls.items() ]

    start_time = time.time()

    # Download with controlled concurrency
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DOWNLOADS) as executor:

        results = [executor.submit(single_download, arg) for arg in download_args]

        # Master progress bar for overall progress
        with alive_bar(
                total=len(results), title=f"⬇ {folder_name}", spinner="pulse", bar="smooth",
                monitor='[{count} chunks / {total} chunks] {percent}% done',
                stats='[{rate}] [ETA: {eta}]') as master_bar:

            for future in as_completed(results):
                filepath, error, file_size= future.result()

                # Get batch download speed
                _download_speed(downloaded=file_size, time_started=start_time, bar=master_bar)

                if filepath:
                    downloaded.append(filepath)

                else:
                    failed.append(error)

                master_bar()

    logger.info(f"Successfully downloaded {len(downloaded)}/{len(batch_urls)} files")

    if failed:
        logger.warning(f"{len(failed)} files failed:")

        for fail in failed:
            logger.warning(f"  - {fail}")

    return downloaded
