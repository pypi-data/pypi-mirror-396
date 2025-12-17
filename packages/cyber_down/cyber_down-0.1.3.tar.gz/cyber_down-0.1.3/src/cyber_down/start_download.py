import time
import logging

from typing import Tuple, List, Dict, Optional

from cyber_down.handlers.decorators import retry
from cyber_down.handlers.configs import logging_config
from cyber_down.handlers.downloaders import batch_download, single_download

# CONFIGURE LOGGING
logger = logging_config(__name__, level=logging.DEBUG)


# Downloader
@retry(5, 15, ConnectionError)
def start_download(
        ext: Optional[str] = '',
        folder: Optional[str] = None,
        file_data: Optional[Tuple[str, str]] = None,
        batch_urls: Optional[Dict[str, str]] = None,
) -> List[str] | Tuple[str, str]:
    """
    Start downloading file(s) with optimized parallel processing

    :param ext: File extension (with dot)
    :param folder: Folder name for batch downloads (None for single file downloads)
    :param file_data: (filename, url) tuple for single file download
    :param batch_urls: {filename: url, ...} dictionary for batch download
    :return: List of downloaded filepaths or single (filepath, error) tuple
    """

    try:
        logger.info("Starting download")
        start_time = time.time()

        if batch_urls: # Batch download - use folder name
            if not folder:
                folder = "batch_download"

            download_result = batch_download(ext, folder, batch_urls)

        elif file_data: # Single file download - no folder (downloads to base directory)
            args = (ext, file_data, None, False)
            download_result = single_download(args)

        else:
            logger.critical("No valid file data provided")
            return []

        end_time = time.time()
        elapsed = (end_time - start_time) / 60

        logger.info(f"Download completed in {elapsed:.2f} min(s)")

        return download_result

    except Exception as e:
        logger.error(f"Error during download: {e}", exc_info=True)
        return []
