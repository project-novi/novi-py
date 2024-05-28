from pathlib import Path
from uuid import UUID

from typing import Union

_storage_path = Path('storage')


def set_storage_path(path: Path) -> None:
    global _storage_path
    _storage_path = path


def object_path(id: Union[UUID, str], variant: str = 'original') -> Path:
    name = str(id) if variant == 'original' else f'{id}.{variant}'
    return _storage_path / name
