import grpc
import inspect
import sys

from structlog import get_logger
from functools import cache, wraps

from .proto import novi_pb2

_METADATA_KEYS = {'argument', 'permission', 'id', 'tag', 'type'}

lg = get_logger()


@cache
def _error_dict():
    errors = [
        NoviError,
        UnsupportedError,
        DBError,
        IOError,
        PermissionDeniedError,
        IdentityExpiredError,
        FileNotFoundError,
        FunctionNotFoundError,
        ObjectNotFoundError,
        InvalidArgumentError,
        InvalidCredentialsError,
        InvalidTagError,
        InvalidObjectError,
        InvalidStateError,
    ]
    return {error.KIND: error for error in errors}


def _error_by_kind(kind):
    return _error_dict().get(kind, NoviError)


# Decorator to convert grpc.RpcError to NoviError
def handle_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            resp = func(*args, **kwargs)
            if inspect.isawaitable(resp):

                async def awaitable_wrapper():
                    try:
                        return await resp
                    except grpc.RpcError as e:
                        raise NoviError.from_grpc(e) from None

                return awaitable_wrapper()

            return resp

        except grpc.RpcError as e:
            raise NoviError.from_grpc(e) from None

    return wrapper


class NoviError(Exception):
    KIND = 'Unspecified'

    metadata: dict[str, str]

    def __init__(self, message: str, metadata: dict[str, str] = {}):
        self.metadata = metadata
        super().__init__(message)

    def __str__(self):
        s = self.KIND + ': ' + super().__str__()
        if self.metadata:
            s += ' ' + str(self.metadata)
        return s

    @staticmethod
    def from_pb(pb: novi_pb2.Error):
        error = _error_by_kind(pb.kind)
        return error(pb.message, pb.metadata)

    @staticmethod
    def from_grpc(exc: grpc.RpcError):
        metadata = exc.trailing_metadata()
        metadata = {datum[0]: datum[1] for datum in metadata}
        error = _error_by_kind(metadata.get('kind', ''))
        return error(
            str(exc.details()),
            {k: v for k, v in metadata.items() if k in _METADATA_KEYS},
        )

    def to_pb(self) -> novi_pb2.Error:
        return novi_pb2.Error(
            kind=self.KIND,
            message=super().__str__(),
            metadata=self.metadata,
        )

    @staticmethod
    def current(message: str | None = None) -> 'NoviError':
        if message is not None:
            lg.exception(message)
        exc_info = sys.exc_info()
        if isinstance(exc_info[1], NoviError):
            return exc_info[1]

        return NoviError(
            message=str(exc_info[1]), metadata={'type': exc_info[0].__name__}
        )


class DBError(NoviError):
    KIND = 'DBError'


class IOError(NoviError):
    KIND = 'IOError'


class UnsupportedError(NoviError):
    KIND = 'Unsupported'


class IdentityExpiredError(NoviError):
    KIND = 'IdentityExpired'


class PermissionDeniedError(NoviError):
    KIND = 'PermissionDenied'


class FileNotFoundError(NoviError):
    KIND = 'FileNotFound'


class FunctionNotFoundError(NoviError):
    KIND = 'FunctionNotFound'


class ObjectNotFoundError(NoviError):
    KIND = 'ObjectNotFound'


class InvalidArgumentError(NoviError):
    KIND = 'InvalidArgument'


class InvalidCredentialsError(NoviError):
    KIND = 'InvalidCredentials'


class InvalidTagError(NoviError):
    KIND = 'InvalidTag'


class InvalidObjectError(NoviError):
    KIND = 'InvalidObject'


class InvalidStateError(NoviError):
    KIND = 'InvalidState'
