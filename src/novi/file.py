from .errors import InvalidStateError


_ipfs_gateway: str | None = None


def set_ipfs_gateway(gateway: str):
    global _ipfs_gateway
    _ipfs_gateway = gateway


def get_ipfs_gateway() -> str:
    if _ipfs_gateway is None:
        raise InvalidStateError('IPFS gateway not set')

    return _ipfs_gateway
