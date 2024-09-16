"""Codec constants."""

__all__ = (
    'Constants',
    )

from .. import cfg

from . import lib
from . import typ


def _isoformat_encoder(
    o: lib.datetime.datetime | lib.datetime.date | lib.datetime.time
    ) -> str:
    return o.isoformat()


class Constants(cfg.Constants):
    """Constant values shared across core codecs modules."""

    ENCODERS: dict[
        type[lib.t.Any],
        lib.t.Callable[[lib.t.Any], typ.Serial]
        ] = {
            bytes: str,
            lib.datetime.date: _isoformat_encoder,
            lib.datetime.datetime: _isoformat_encoder,
            lib.datetime.time: _isoformat_encoder,
            lib.datetime.timedelta: lambda td: getattr(td, 'total_seconds')(),
            lib.decimal.Decimal: float,
            lib.enum.Enum: lambda o: getattr(o, 'value'),
            frozenset: list,
            lib.collections.deque: list,
            lib.types.GeneratorType: list,
            lib.ipaddress.IPv4Address: str,
            lib.ipaddress.IPv4Interface: str,
            lib.ipaddress.IPv4Network: str,
            lib.ipaddress.IPv6Address: str,
            lib.ipaddress.IPv6Interface: str,
            lib.ipaddress.IPv6Network: str,
            lib.pathlib.Path: str,
            lib.re.Pattern: lambda o: getattr(o, 'pattern'),
            set: list,
            lib.uuid.UUID: str,
            }
