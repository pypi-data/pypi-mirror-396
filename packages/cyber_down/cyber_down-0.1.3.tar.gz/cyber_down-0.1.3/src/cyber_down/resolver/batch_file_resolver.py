import json
from os import getenv
from pathlib import Path
from typing import Dict

from cyber_down.resolver.single_file_resolver import _get_base_download_dir

# RESOLVE BATCH DOWNLOAD FOLDER ( CYBER_DOWNLOADS / BATCH_DOWNLOAD_FOLDER)

# Create folder for batch downloads in base download directory
def resolve_batch_download_dir(folder_name: str) -> str:
    """
    Resolve the absolute path for a batch download folder

    :param folder_name: Name of the folder for batch downloads
    :return: Absolute path string for the batch folder
    """

    base_dir = _get_base_download_dir()

    batch_folder = base_dir / folder_name
    batch_folder.mkdir(parents=True, exist_ok=True)

    return str(batch_folder)


# RESOLVE  BATCHLINK FOLDER AND BATCHLINK FILES ( ~/ BATCHLINKS)

# Resolve base download folder
def _get_base_batchlink_dir() -> Path:
    """
    Get the base batchlink directory from environment or use default

    :return: Base batchlink directory path
    """

    base_dir = getenv('BATCHLINKS_DIR', str(Path.home() / 'Batchlinks'))

    return Path(base_dir)


# Create batch file  for the batch folder
def _resolve_batchlink_filepath(filename: str) -> Path:
    """
    Returns the absolute path of a batch file given a filename

    :param filename: Name of the batch file
    :return: Absolute path to batch file
    """

    base_dir = _get_base_batchlink_dir()
    base_dir.mkdir(parents=True, exist_ok=True)

    clean_filename = filename.replace(" ", "_").replace(".", "_")

    filepath = base_dir / f'{clean_filename}_batch.json' # BATCHLINKS/FILENAME_BATCH

    return filepath


# Write batch data to file
def write_batchlink_file(filename: str, links: Dict[str, str]) -> Path:
    """
    Write batch download data to a JSON file

    :param filename: Name for the batch file
    :param links: Dictionary of {filename: url}
    :return: Path to created batch file
    """

    batch_file = _resolve_batchlink_filepath(filename)
    batch_data = json.dumps(links, indent=2)

    with batch_file.open('w') as file:
        file.write(batch_data)

    return batch_file


# Return file data
def get_batchlink_file(filename: str) -> Dict[str, str]:
    """
    Read and return the contents of a batchlink file

    :param filename: Name of the batch file or absolute path
    :return: Dictionary of {filename: url}
    """

    # Check if filename is already an absolute path
    file_path = Path(filename)

    if file_path.is_absolute() and file_path.exists():
        with file_path.open('r') as file:
            return json.load(file)

    # Otherwise, resolve as batchlink file
    batch_file = _resolve_batchlink_filepath(filename)

    if not batch_file.exists():
        raise FileNotFoundError(f"Batch file not found: {batch_file}")

    with batch_file.open('r') as file:
        return json.load(file)

# Example usage and test case
def test():
    filename = input('Enter filename: ')
    print(get_batchlink_file(filename=filename))


if __name__ == '__main__':
    test()