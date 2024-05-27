from .proto import novi_pb2

from datetime import datetime, timezone
from uuid import UUID


def dt_to_timestamp(dt: datetime) -> int:
    return int(dt.timestamp()) * 1_000_000 + dt.microsecond


def dt_from_timestamp(ts: int) -> datetime:
    dt = datetime.fromtimestamp(ts // 1_000_000, tz=timezone.utc)
    return dt.replace(microsecond=ts % 1_000_000)


def uuid_from_pb(pb: novi_pb2.UUID) -> UUID:
    return UUID(int=pb.hi << 64 | pb.lo)


def uuid_to_pb(uuid: UUID) -> novi_pb2.UUID:
    return novi_pb2.UUID(hi=uuid.int >> 64, lo=uuid.int & (1 << 64) - 1)


def rfc3339(dt: datetime) -> str:
    return dt.isoformat()[:-6] + 'Z'
