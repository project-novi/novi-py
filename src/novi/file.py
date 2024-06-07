from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlparse

from typing import BinaryIO

_url_handlers = {}

_storage_path = Path('storage')


def default_url_handler(url: str) -> BinaryIO:
    return urlopen(url)


def open_url(url: str, *args, **kwargs):
    parsed = urlparse(url)
    handler = _url_handlers.get(parsed.scheme, default_url_handler)
    return handler(url, *args, **kwargs)


def install_url_handler(scheme: str, handler) -> BinaryIO:
    _url_handlers[scheme] = handler


def set_storage_path(path: Path) -> None:
    global _storage_path
    _storage_path = path

    def file_url_handler(url: str) -> BinaryIO:
        return parse_file_url(url).open('rb')

    install_url_handler('file', file_url_handler)


def parse_file_url(url: str) -> Path:
    parsed = urlparse(url)
    assert parsed.scheme == 'file'
    id = parsed.netloc
    variant = parsed.path.lstrip('/')
    name = id if variant == 'original' else f'{id}.{variant}'
    return _storage_path / name
