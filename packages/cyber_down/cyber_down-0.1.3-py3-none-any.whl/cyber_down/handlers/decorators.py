import os
import time
import logging

from pathlib import Path
from functools import wraps
from httpcore import TimeoutException

from cyber_down.handlers.configs import logging_config

# CONFIGURE LOGGING
logger = logging_config(__name__, level=logging.DEBUG)


# Retry a failed scraper
def retry(retries=5, delay=5, exceptions=(ConnectionError, TimeoutException), backoff=1.0):
    """
    Retry decorator with proper exception handling and backoff.

    Args:
        retries: Number of retry attempts
        delay: Initial delay between retries
        exceptions: Tuple of exception types to catch and retry
        backoff: Multiplier for delay (1.0 = fixed, 2.0 = exponential)
    """

    def decorator(func):
        # noinspection PyInconsistentReturns
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(retries + 1):  # +1 for initial attempt
                try:
                    return func(*args, **kwargs)  # Run the function

                except exceptions as e:
                    if attempt == retries:  # Last attempt failed
                        logger.warning(f"{func.__name__} failed after {retries} retries")
                        raise e  # Re-raise the actual exception

                    logger.debug(f"{func.__name__} failed attempt {attempt + 1}/{retries + 1}: {e}")
                    logger.info(f"Waiting {current_delay} seconds before retry...")

                    time.sleep(current_delay)
                    current_delay *= backoff  # Apply backoff
                except Exception as e:
                    # Don't retry programming errors
                    logger.error(f"{func.__name__} failed with non-retryable error: {e}", exc_info=True)
                    raise e

        return wrapper

    return decorator


# Resume a failed or paused download using PSD
def resume_chunk_download(func):
    """
    Decorator that allows resuming a partial chunk download
    Checks if a .partN file exists and resumes from that point

    :param func: The download function to wrap
    """

    @wraps(func)
    def wrapper(download_arg, **kwargs):
        # Unpack the download argument tuple
        url, filepath, start, end, chunk_id = download_arg

        # Construct temp file path
        file_path = Path(filepath)
        part_path = file_path.parent / f"{file_path.name}.part{chunk_id}"

        # If partial file exists, find out how much is already downloaded
        if part_path.exists():
            already_downloaded = os.path.getsize(part_path)

        else:
            already_downloaded = 0

        # Only resume if we have not already finished this chunk
        if already_downloaded > 0 and (start + already_downloaded) <= end:
            new_start = start + already_downloaded
            logger.info(f"[Part {chunk_id}] Resuming from byte {new_start}")

            # Update Range header
            headers = kwargs.get("headers", {})
            headers["Range"] = f"bytes={new_start}-{end}"
            kwargs["headers"] = headers

            new_download_arg = (url, filepath, new_start, end, chunk_id) # New start for chunk

            return func(new_download_arg, **kwargs)

        else:
            return func(download_arg, **kwargs)

    return wrapper


# Resume a failed or paused download using SD
def resume_streaming_download(func):
    """
    Decorator that allows resuming a partial streaming download
    Checks if a .part file exists and resumes from that point using Range header

    :param func: The streaming download function to wrap
    """

    @wraps(func)
    def wrapper(filename, link, filepath, master_progress_bar, **kwargs):

        file_path = Path(filepath)
        temp_path = file_path.parent / f"{file_path.name}.part"

        if temp_path.exists():
            already_downloaded = os.path.getsize(temp_path)

        else:
            already_downloaded = 0

        if already_downloaded > 0:
            resume = True
            logger.info(f"[{filename}] Resuming from byte {already_downloaded}")

        else:
            resume = False

        # Call the original function with resume information
        return func(
            filename=filename,
            link=link,
            filepath=filepath,
            master_progress_bar=master_progress_bar,
            resume_mode=resume,
            temp_path=temp_path,
            already_downloaded=already_downloaded,
            **kwargs
        )

    return wrapper
