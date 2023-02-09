import random
from string import ascii_letters as letters
from pathlib import Path
from tempfile import gettempdir as _gettempdir


def get_temp_download_directory(random_id_length: int = 17) -> Path:
    random_id = "".join(random.choice(letters) for i in range(random_id_length))
    return Path(_gettempdir()) / f"deprag_downloader{random_id}"


def get_download_directory(download_directory: Path = None) -> Path:
    download_directory = (
        download_directory
        if download_directory is not None
        else get_temp_download_directory()
    ).resolve()
    download_directory.mkdir(parents=True, exist_ok=True)
    return download_directory
