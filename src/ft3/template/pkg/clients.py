"""A module containing an example database integration."""

__all__ = (
    'DatabaseClient',
    )

from ... import Object

from . import lib
from . import typ


class DatabaseClient:
    """A simple, example database client."""

    DATA: dict[str, Object] = {}

    @classmethod
    def delete_one(cls, _id: str) -> lib.t.Optional[lib.Never]:
        """Delete an existing record from database."""

        if _id in cls.DATA:
            del cls.DATA[_id]
        else:  # pragma: no cover
            raise FileNotFoundError

        return None

    @classmethod
    def find_many(cls, query: dict[str, lib.t.Any]) -> list[Object]:
        """Get records from database that match the query."""

        return [
            record
            for record
            in cls.DATA.values()
            if all(record[k] == v for k, v in query.items())
            ]

    @classmethod
    def find_one(cls, _id: str) -> lib.t.Optional[Object]:
        """Get one record from database by primary key."""

        return cls.DATA.get(_id)

    @classmethod
    def insert_one(cls, record: typ.ObjectType) -> typ.ObjectType:
        """Add record to database."""

        cls.DATA[record[record.hash_fields[0]]] = record
        return record

    @classmethod
    def update_one(cls, record: typ.ObjectType) -> typ.ObjectType:
        """Update existing record in database."""

        cls.DATA[record[record.hash_fields[0]]] = record
        return record
