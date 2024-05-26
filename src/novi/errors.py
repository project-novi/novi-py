import grpc
import sys

from functools import wraps

from . import novi_pb2

from typing import Dict

_METADATA_KEYS = {'permission', 'id', 'tag', 'type'}


def _error_dict():
    return {
        'Unspecified': NoviError,
        'DBError': DBError,
        'IOError': IOError,
        'PermissionDenied': PermissionDeniedError,
        'IdentityExpired': IdentityExpiredError,
        'FunctionNotFound': FunctionNotFoundError,
        'ObjectNotFound': ObjectNotFoundError,
        'InvalidArgument': InvalidArgumentError,
        'InvalidCredentials': InvalidCredentialsError,
        'InvalidTag': InvalidTagError,
        'InvalidObject': InvalidObjectError,
        'InvalidState': InvalidStateError,
    }


def _error_kind(kind):
    return _error_dict().get(kind, NoviError)


# Decorator to convert grpc.RpcError to NoviError
def handle_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except grpc.RpcError as e:
            raise NoviError.from_grpc(e) from None

    return wrapper


class NoviError(Exception):
    metadata: Dict[str, str]

    def __init__(self, message: str, metadata: Dict[str, str] = {}):
        self.metadata = metadata
        super().__init__(message)

    def __str__(self):
        s = super().__str__()
        if self.metadata:
            s += ' ' + str(self.metadata)
        return s

    @staticmethod
    def from_pb(pb: novi_pb2.Error):
        error = _error_kind(pb.kind)
        return error(pb.message, pb.metadata)

    @staticmethod
    def from_grpc(exc: grpc.RpcError):
        metadata = exc.trailing_metadata()
        metadata = {datum.key: datum.value for datum in metadata}
        error = _error_kind(metadata.get('kind', ''))
        return error(
            str(exc.details()),
            {k: v for k, v in metadata.items() if k in _METADATA_KEYS},
        )

    def error_kind(self) -> str:
        for kind, error in _error_dict().items():
            if isinstance(self, error):
                return kind

        return 'Unspecified'

    def to_pb(self) -> novi_pb2.Error:
        return novi_pb2.Error(
            kind=self.error_kind(),
            message=super().__str__(),
            metadata=self.metadata,
        )

    @staticmethod
    def current() -> 'NoviError':
        exc_info = sys.exc_info()
        if isinstance(exc_info[1], NoviError):
            return exc_info[1]

        return NoviError(
            message=str(exc_info[1]), metadata={'type': exc_info[0].__name__}
        )


class DBError(NoviError):
    pass


class IOError(NoviError):
    pass


class IdentityExpiredError(NoviError):
    pass


class PermissionDeniedError(NoviError):
    pass


class FunctionNotFoundError(NoviError):
    pass


class ObjectNotFoundError(NoviError):
    pass


class InvalidArgumentError(NoviError):
    pass


class InvalidCredentialsError(NoviError):
    pass


class InvalidTagError(NoviError):
    pass


class InvalidObjectError(NoviError):
    pass


class InvalidStateError(NoviError):
    pass
