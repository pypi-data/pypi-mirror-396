import time
import logging
import requests

from pathlib import Path
from typing import Tuple, List
from alive_progress import alive_bar
from concurrent.futures import ThreadPoolExecutor, as_completed

from cyber_down.handlers.configs import logging_config
from cyber_down.handlers.download_metrics import _download_speed
from cyber_down.handlers.decorators import resume_chunk_download
from cyber_down.handlers.constants import THREADS, TIMEOUT, CHUNK_SIZE

# CONFIGURE LOGGING
logger = logging_config(__name__, level=logging.DEBUG)


# Check if multi-chunk is available
def _check_download_capability(url: str) -> Tuple[bool, int, bool]:
    """
    Check if URL supports range requests and get file size

    :param url: URL to check
    :return: (is_accessible, file_size, supports_range)
    """

    try:
        with requests.head(url=url, timeout=TIMEOUT, allow_redirects=True) as response:
            if response.status_code not in (200, 302):
                logger.warning(
                    f"HEAD request failed with status {response.status_code}, trying GET"
                )
                response = requests.get(url, stream=True, timeout=TIMEOUT)
                response.raise_for_status()

            file_size = int(response.headers.get("content-length", 0))
            supports_range = (
                response.headers.get("accept-ranges", "").lower() == "bytes"
            )

            return True, file_size, supports_range

    except Exception as e:
        logger.error(f"Error checking URL capability: {e}")
        return False, 0, False


# Download a single chunk
@resume_chunk_download
def _download_chunk(download_arg: Tuple[str, str, int, int, int]) -> Tuple[bool, int, int, Path, int]:
    """
    Download a specific chunk of the file

    :param download_arg: (url, filepath, start, end, chunk_id)
    :return:
        (success = True or false,
        start = where to start download. If resuming; adds the already downloaded bytes,
        end = End of the file,
        temp_filename = the part file,
        written = The number of bytes written)
    """

    url, filepath, start, end, chunk_id = download_arg

    # Convert to Path and create temp file in same directory as final file
    file_path = Path(filepath)
    temp_file = file_path.parent / f"{file_path.name}.part{chunk_id}"

    # Setup headers
    headers = {
        "Range": f"bytes={start}-{end}",
        "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36"
            ),
        "Accept": "*/*",
        "Accept-Encoding": "identity",
        "Connection": "keep-alive"
    }

    try:
        with requests.get(url=url, stream=True, timeout=TIMEOUT, headers=headers, allow_redirects=True) as response:

            if response.status_code not in (200, 206):
                logger.error(f"Chunk {chunk_id} failed with status {response.status_code}")

                return False, 0, 0, temp_file, 0

            with temp_file.open('ab') as file: # Append data so it can resume if needed

                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE): # Add chunk data to temp file
                        if chunk:
                            file.write(chunk)
                            written = len(chunk)

            return True, start, end, temp_file, written

    except Exception as e:
        logger.error(f"Error downloading chunk {chunk_id}: {e}")

        return False, 0, 0, temp_file, 0


# Get all chunks with their respective metadata to use as download arguments
def _get_chunk_metadata(url: str, filepath: str, file_size: int,
                        num_threads: int =THREADS) -> List[Tuple[str, str, int, int, int]]:
    """
    Get chunk metadata to pass as an argument for download_multiple_chunks()

    :param url: URL to download from
    :param filepath: Base file path
    :param file_size: File size
    :param num_threads: Number of threads
    :return: Cyber_Down args
    """

    chunk_size = file_size // num_threads # File is broken into chunks, and each thread downloads a chunk of this size*
    download_args = [] # Tuple of args for the download_chunk function

    for chunk_id in range(num_threads):
        start = chunk_id * chunk_size  # Where to start downloading
        # Makes the last chunk larger if there are any remaining bytes
        end = ( (start + chunk_size) - 1 if chunk_id < (num_threads - 1) else file_size - 1)

        download_args.append((url, filepath, start, end, chunk_id))

    return download_args


# Remove all temp files
def _cleanup_temp_files(temp_files: List[Path]) -> None:
    """
    Remove all temporary chunk files

    :param temp_files: List of temporary file paths to remove
    """

    for temp_file in temp_files:
        try:
            if temp_file.exists():
                temp_file.unlink()
                logger.debug(f"Cleaned up temp file: {temp_file}")

            else:
                logger.error(f"Temp file: {temp_file} does not exist")

        except Exception as e:
            logger.warning(f"Failed to remove temp file {temp_file}: {e}")
            continue


# Merge all individual chunks into one file
def _merge_chunks(filepath: str, temp_files: List[Path]) -> bool:
    """
    Merge all downloaded chunks into final file

    :param filepath: Final output filepath (string)
    :param temp_files: List of temporary chunk files to merge
    :return: Success status
    """

    final_path = Path(filepath)

    try:
        with final_path.open("wb") as full_file:

            for temp_file in sorted(temp_files): # Ensure chunk order when adding temp files
                if temp_file.exists():
                    with temp_file.open("rb") as chunk:

                        full_file.write(chunk.read()) # Add the chunk to the full file

                    temp_file.unlink(missing_ok=True)  # Delete temp file

                else:
                    logger.error(f"Missing chunk file: {temp_file}")
                    return False

        logger.info(f"Successfully merged chunks into: {final_path}")
        return True

    except Exception as e:
        logger.error(f"Error merging chunks: {e}")

        _cleanup_temp_files(temp_files= temp_files)
        return False


# Parallel segmented downloading
def _download_multiple_chunks(
        url: str, filepath: str, file_size: int, num_threads: int =THREADS,
        master_progress_bar:bool= False) -> bool:
    """
    Execute chunked download with progress tracking

    :param url: URL to download from
    :param filepath: Path where file should be saved
    :param file_size: Total size of file in bytes
    :param num_threads: Number of parallel download threads
    :return: Success status
    """

    download_args = _get_chunk_metadata(
        url=url, filepath=filepath, file_size=file_size, num_threads=num_threads) # Get download_chunk args

    temp_files = []
    total_downloaded = 0 # Shared memory

    start_time = time.time()

    try:
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            results = [executor.submit(_download_chunk, arg) for arg in download_args]

            if not master_progress_bar:
                with alive_bar(
                        total=len(results), title=f"⬇ {filepath}", spinner="pulse", bar="smooth",
                        monitor='[{count} chunks / {total} chunks] {percent}% done',
                        stats='[{rate}] [ETA: {eta}]') as progress_bar:

                    # Process each chunk after it finishes downloading
                    for future in as_completed(results):
                        success, start, end, temp_file, written = future.result() # Unpack chunk data from future

                        temp_files.append(temp_file)
                        # Get download speed
                        total_downloaded += written
                        _download_speed(downloaded=total_downloaded, time_started=start_time, bar=progress_bar)

                        if success:
                            logger.debug(f"Downloaded chunk: {temp_file}")

                        else:
                            logger.error(f"{temp_file} download failed.")

                        progress_bar()

            # Don't display project bar if inside the main progress bar (yet...)
            else:
                # Process each chunk after it finishes downloading
                for future in as_completed(results):
                    success, start, end, temp_file, _ = future.result()  # Unpack chunk data from future

                    temp_files.append(temp_file)

                    if success:
                        logger.debug(f"Downloaded chunk: {temp_file}")

                    else:
                        logger.error(f"{temp_file} download failed.")

        file_merged = _merge_chunks(filepath=filepath, temp_files=temp_files)

        return file_merged

    except Exception as e:
        logger.error(f"Error downloading multiple chunks: {e}")
        return False
