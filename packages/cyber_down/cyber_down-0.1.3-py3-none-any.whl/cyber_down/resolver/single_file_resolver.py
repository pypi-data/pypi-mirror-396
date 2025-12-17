from os import getenv
from pathlib import Path

# Resolve base download folder
def _get_base_download_dir() -> Path:
    """
    Get the base download directory from environment or use default

    :return: Base download directory path
    """

    base_dir = getenv('CYBER_DOWNLOADS_DIR', str(Path.home() / 'Cyber_Downloads'))

    return Path(base_dir)


#  Resolve file path inside download folder
def resolve_single_file_path(filename: str, ext: str = '') -> str:
    """
    Resolve the absolute path for a single file download

    :param filename: Name of the file.
    :param ext: File extension (with dot. e.g, .mp4)
    :return: Absolute path string for the file
    """

    base_dir = _get_base_download_dir()
    base_dir.mkdir(parents=True, exist_ok=True)

    clean_filename = str(filename).replace(" ", "_").replace(".", "_")

    if ext:
        full_filename = f"{clean_filename}{ext}"

    else:
        full_filename = clean_filename

    filepath = base_dir / full_filename # CYBER_DOWNLOADS / FILENAME.EXT

    return str(filepath)


# Resolve batch folder / filepath inside download folder
def resolve_batch_file_path(folder_name: str, filename: str, ext: str = '') -> str:
    """
    Resolve the absolute path for a file within a batch download folder

    :param folder_name: Name of the batch folder
    :param filename: Name of the file.
    :param ext: File extension (with dot. e.g, .mp4)
    :return: Absolute path string for the file
    """

    base_dir = _get_base_download_dir()

    batch_folder = base_dir / folder_name
    batch_folder.mkdir(parents=True, exist_ok=True)

    clean_filename = str(filename).replace(" ", "_").replace(".", "_")

    if ext:
        full_filename = f"{clean_filename}{ext}"

    else:
        full_filename = clean_filename

    bath_filepath = batch_folder / full_filename # CYBER_DOWNLOADS / BATCH FOLDER / FILENAME.EXT

    return str(bath_filepath)
