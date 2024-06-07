from pathlib import Path
from urllib.parse import urlparse

_storage_path = Path('storage')


def set_storage_path(path: Path) -> None:
    global _storage_path
    _storage_path = path


def parse_file_url(url: str) -> Path:
    parsed = urlparse(url)
    assert parsed.scheme == 'file'
    id = parsed.netloc
    variant = parsed.path.lstrip('/')
    name = id if variant == 'original' else f'{id}.{variant}'
    return _storage_path / name
