import struct


class ParseError(Exception):
    pass


class CGameDataParser:
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0
        self.attrs = []  # LoadData
        self.records = []  # LoadArchieveRec

    def read_bytes(self, n: int) -> bytes:
        if self.offset + n > len(self.data):
            raise ParseError("Out range")
        b = self.data[self.offset : self.offset + n]
        self.offset += n
        return b

    def read_int32(self) -> int:
        return struct.unpack_from("<i", self.read_bytes(4))[0]

    def read_uint32(self) -> int:
        return struct.unpack_from("<I", self.read_bytes(4))[0]

    def read_int64(self) -> int:
        return struct.unpack_from("<q", self.read_bytes(8))[0]

    def read_uint8(self) -> int:
        return struct.unpack_from("<B", self.read_bytes(1))[0]

    def read_uint64(self) -> int:
        return struct.unpack_from("<Q", self.read_bytes(8))[0]

    def read_utf8(self) -> str:
        len = self.read_uint32()
        data = self.read_bytes(len)
        return data.decode("utf-8", errors="replace")[:-1]

    def read_utf16(self) -> str:
        len = self.read_uint32()
        data = self.read_bytes(len)
        return data.decode("utf-16", errors="replace")[:-1]

    def parse(self):
        attr_count = self.read_int32()
        print(f"Attr Count: {attr_count}")

        for i in range(attr_count):
            attr_name = self.read_utf8()
            attr_value_type = self.read_int32()

            attr_value = None
            if attr_value_type == 2:
                attr_value = self.read_int32()
                self.read_uint8()
            elif attr_value_type == 3:
                attr_value = self.read_int64()
                self.read_uint8()
            elif attr_value_type == 4:
                attr_value = self.read_uint64()
                self.read_uint8()
            elif attr_value_type == 5:
                self.read_bytes(4)
                self.read_uint8()
            elif attr_value_type == 6:
                self.read_bytes(8)
                self.read_uint8()
            elif attr_value_type == 7:
                attr_value = self.read_int32()
                self.read_uint8()
            elif attr_value_type == 8:
                attr_value = self.read_utf16()
                self.read_uint8()
            else:
                print(f"Unknown Attr Type: {attr_value_type}")
                continue

            self.attrs.append(
                {
                    "key": attr_name,
                    "value": attr_value,
                }
            )
            print(f"  Attr[{i}]: key={attr_name}, value={attr_value}")

        record_count = self.read_int32()
        print(f"Record Count: {record_count}")

        for i in range(record_count):
            rec = self.parse_archive_rec()
            if rec is None:
                raise ParseError(f"第 {i} 条记录解析失败")
            self.records.append(rec)

        return True

    def parse_archive_rec(self):
        rec_name = self.read_utf8()
        print(f"  [Record] name={rec_name}")

        unk1 = self.read_int32()
        row_count = self.read_int32()
        col_count = self.read_int32()
        unk2 = self.read_uint8()

        print(f"    unk1={unk1} rows={row_count} cols={col_count} unk2={unk2}")

        if col_count < 1 or col_count > 256:
            raise ParseError("Out range")

        col_types = [self.read_uint8() for _ in range(col_count)]

        rows = []
        for r in range(row_count):
            row = []
            for c in range(col_count):
                t = col_types[c]
                if t == 2:
                    val = self.read_int32()
                elif t == 3:
                    val = self.read_int64()
                elif t == 4:
                    val = self.read_uint64()
                elif t == 5:
                    val = self.read_int32()
                elif t == 6:
                    val = self.read_int64()
                elif t == 7:
                    val = self.read_utf8()
                elif t == 8:
                    val = self.read_utf16()
                else:
                    print(f"    Unknown column type {t}: row={r}, col={c}")
                    val = None

                row.append({"type": t, "value": val})

            rows.append(row)

        for r, row in enumerate(rows):
            # for c, item in enumerate(row):
            #     print(f"    Col[{c}]: {item['type']} {item['value']}")

            print(f"    Row[{r}]: {[str(item['value']) for item in row]}")

        return {
            "name": rec_name,
            "unk1": unk1,
            "unk2": unk2,
            "rows": rows,
        }


def parse_file(filepath: str):
    with open(filepath, "rb") as f:
        data = f.read()
    parser = CGameDataParser(data)
    try:
        parser.parse()
    except ParseError as e:
        print(f"Parse Error: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        parse_file(sys.argv[1])
    else:
        print("Usage: python parse_game_data.py <game_data_file>")
