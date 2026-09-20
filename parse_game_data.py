import logging
import struct
import sys
from collections.abc import Callable
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


class CGameDataParser:
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0
        self.attrs = []
        self.records = []

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

    def _unpack(self, fmt: str, n: int) -> Any:
        if self.offset + n > len(self.data):
            raise ParseError("Out range")
        value = struct.unpack_from(fmt, self.data, self.offset)[0]
        self.offset += n
        return value

    def read_uint8(self) -> int:
        return self._unpack("<B", 1)

    def read_int32(self) -> int:
        return self._unpack("<i", 4)

    def read_uint32(self) -> int:
        return self._unpack("<I", 4)

    def read_int64(self) -> int:
        return self._unpack("<q", 8)

    def read_uint64(self) -> int:
        return self._unpack("<Q", 8)

    def read_float(self) -> float:
        return self._unpack("<f", 4)

    def read_double(self) -> float:
        return self._unpack("<d", 8)

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
        self._parse_attrs()
        self._parse_records()

    def _parse_attrs(self):
        attr_count = self.read_int32()
        logger.info("Attr Count: %d", attr_count)

        for i in range(attr_count):
            attr_name = self.read_string()
            attr_value_type = self.read_int32()
            attr_value = self.read_value(attr_value_type)
            self.read_uint8()

            self.attrs.append(
                {
                    "key": attr_name,
                    "value": attr_value,
                }
            )
            print(f"  Attr[{i}]: key={attr_name}, value={attr_value}")

    def _parse_records(self):
        record_count = self.read_int32()
        logger.info("Record Count: %d", record_count)

        for i in range(record_count):
            rec = self.parse_archive_rec()
            if rec is None:
                raise ParseError(f"第 {i} 条记录解析失败")
            self.records.append(rec)

        return True

    def parse_archive_rec(self):
        rec_name = self.read_string()
        unk1 = self.read_int32()
        row_count = self.read_int32()
        col_count = self.read_int32()
        self.read_uint8()

        print(
            f"  [Record] name={rec_name} unk1={unk1} rows={row_count} cols={col_count}"
        )

        if col_count < 1 or col_count > 256:
            raise ParseError("Out range")

        col_types = [self.read_uint8() for _ in range(col_count)]

        rows = []
        for r in range(row_count):
            row = []
            for c in range(col_count):
                t = col_types[c]

                try:
                    value = self.read_value(t)
                except ParseError:
                    logger.error(f"Unknown column type {t}: row={r}, col={c}")
                    raise

                row.append({"type": t, "value": value})

            rows.append(row)

        for r, row in enumerate(rows):
            # for c, item in enumerate(row):
            #     print(f"    Col[{c}]: {item['type']} {item['value']}")

            print(f"    Row[{r}]: {[str(item['value']) for item in row]}")

        return {
            "name": rec_name,
            "unk1": unk1,
            "rows": rows,
        }


def parse_file(filepath: str):
    with open(filepath, "rb") as f:
        data = f.read()
    parser = CGameDataParser(data)
    try:
        parser.parse()
    except ParseError as e:
        logger.error("Parse Error: %s", e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if len(sys.argv) > 1:
        parse_file(sys.argv[1])
    else:
        print("Usage: python parse_game_data.py <game_data_file>")
