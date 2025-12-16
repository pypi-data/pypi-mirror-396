import urllib.request
from pathlib import Path


def _download_data(url, overwrite=False):
    data_dir = Path.home() / ".budgetnlp" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    filename = Path(url).name
    file_path = data_dir / filename

    if file_path.exists() and not overwrite:
        return file_path

    print(f"Downloading {filename} dictionary to {file_path}")
    urllib.request.urlretrieve(url, file_path)
    print(file_path)
    return file_path