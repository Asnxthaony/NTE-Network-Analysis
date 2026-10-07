import logging
import struct
import sys
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any

logger = logging.getLogger(__name__)


class RecordType(IntEnum):
    INT32 = 2
    INT64 = 3
    UINT64 = 4
    FLOAT = 5
    DOUBLE = 6
    STRING = 7
    WIDE_STRING = 8


class ParseError(Exception):
    pass


@dataclass(slots=True)
class Attr:
    key: str
    value: Any


@dataclass(slots=True)
class Row:
    values: list[Any]

    def __len__(self) -> int:
        return len(self.values)

    def __iter__(self) -> Iterator[Any]:
        return iter(self.values)

    def __getitem__(self, index: int) -> Any:
        return self.values[index]

    def __repr__(self) -> str:
        return f"Row({self.values!r})"


@dataclass(slots=True)
class Record:
    name: str
    unk1: int
    rows: list[Row]

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def col_count(self) -> int:
        return len(self.rows[0]) if self.rows else 0


@dataclass(slots=True)
class ParsedData:
    attrs: list[Attr] = field(default_factory=list)
    records: list[Record] = field(default_factory=list)


class CGameDataParser:
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0

        self._readers: dict[int, Callable] = {
            RecordType.INT32: self.read_int32,
            RecordType.INT64: self.read_int64,
            RecordType.UINT64: self.read_uint64,
            RecordType.FLOAT: self.read_float,
            RecordType.DOUBLE: self.read_double,
            RecordType.STRING: self.read_string,
            RecordType.WIDE_STRING: self.read_wide_string,
        }

    def read_bytes(self, n: int) -> bytes:
        if self.offset + n > len(self.data):
            raise ParseError("Out range")
        b = self.data[self.offset : self.offset + n]
        self.offset += n
        return b

    def _read(self, fmt: str, n: int) -> Any:
        return struct.unpack(fmt, self.read_bytes(n))[0]

    def read_uint8(self) -> int:
        return self._read("<B", 1)

    def read_int32(self) -> int:
        return self._read("<i", 4)

    def read_uint32(self) -> int:
        return self._read("<I", 4)

    def read_int64(self) -> int:
        return self._read("<q", 8)

    def read_uint64(self) -> int:
        return self._read("<Q", 8)

    def read_float(self) -> float:
        return self._read("<f", 4)

    def read_double(self) -> float:
        return self._read("<d", 8)

    def read_string(self) -> str:
        size = self.read_uint32()
        data = self.read_bytes(size)
        return data.decode("utf-8").strip("\x00")

    def read_wide_string(self) -> str:
        size = self.read_uint32()
        data = self.read_bytes(size)
        return data.decode("utf-16").strip("\x00")

    def read_value(self, record_type: int) -> Any:
        reader = self._readers.get(record_type)
        if reader is None:
            raise ParseError(f"Unknown record type: {record_type}")
        return reader()

    def parse(self):
        return ParsedData(
            attrs=self._parse_attrs(),
            records=self._parse_records(),
        )

    def _parse_attrs(self) -> list[Attr]:
        attr_count = self.read_int32()
        logger.info("Attr Count: %d", attr_count)

        attrs: list[Attr] = []
        for i in range(attr_count):
            attr_name = self.read_string()
            attr_value_type = self.read_int32()
            attr_value = self.read_value(attr_value_type)
            self.read_uint8()

            attrs.append(
                Attr(
                    key=attr_name,
                    value=attr_value,
                )
            )
            logger.debug(f"  Attr[{i}]: key={attr_name}, value={attr_value}")

        return attrs

    def _parse_records(self) -> list[Record]:
        record_count = self.read_int32()
        logger.info("Record Count: %d", record_count)

        records: list[Record] = []
        for i in range(record_count):
            rec = self._parse_single_record()
            if rec is None:
                raise ParseError(f"Failed to parse record at index {i}")
            records.append(rec)

        return records

    def _parse_single_record(self) -> Record:
        record_name = self.read_string()
        unk1 = self.read_int32()
        row_count = self.read_int32()
        col_count = self.read_int32()
        self.read_uint8()

        logger.debug(
            f"  [Record] name={record_name} unk1={unk1} rows={row_count} cols={col_count}"
        )

        if col_count < 1 or col_count > 256:
            raise ParseError("Out range")

        col_types = [self.read_uint8() for _ in range(col_count)]

        rows: list[Row] = []
        for r in range(row_count):
            values: list[Any] = []
            for c, t in enumerate(col_types):
                try:
                    values.append(self.read_value(t))
                except ParseError:
                    logger.error(f"Unknown column type {t}: row={r}, col={c}")
                    raise

            rows.append(Row(values))

        for r, row in enumerate(rows):
            logger.debug(f"    Row[{r}]: {[str(v) for v in row]}")

        return Record(name=record_name, unk1=unk1, rows=rows)


def parse_file(filepath: str):
    with open(filepath, "rb") as f:
        data = f.read()

    return CGameDataParser(data).parse()


def dump(data) -> None:
    for i, attr in enumerate(data.attrs):
        print(f"Attr[{i}]: key={attr.key}, value={attr.value}")

    print()

    for rec in data.records:
        print(
            f"[Record] name={rec.name} unk1={rec.unk1} "
            f"rows={rec.row_count} cols={rec.col_count}"
        )
        for r, row in enumerate(rec.rows):
            print(f"  Row[{r}]: {[str(v) for v in row]}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if len(sys.argv) > 1:
        try:
            parsed = parse_file(sys.argv[1])
        except ParseError as e:
            logger.error("Parse Error: %s", e)

        dump(parsed)

    else:
        print("Usage: python parse_game_data.py <game_data_file>")
