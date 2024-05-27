from pathlib import Path
from uuid import UUID

from typing import Union

# Can be mutated by user
storage_path = Path('storage')


def object_path(id: Union[UUID, str], variant: str = 'original') -> Path:
    name = str(id) if variant == 'original' else f'{id}.{variant}'
    return storage_path / name
