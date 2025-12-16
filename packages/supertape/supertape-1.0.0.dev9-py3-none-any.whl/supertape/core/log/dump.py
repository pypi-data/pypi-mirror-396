import string

PRINTABLE = [c for c in string.printable if ord(c) >= 0x20]


def dump(bytes: list[int], width: int = 16) -> list[str]:
    lines = []
    offset = 0

    while offset < len(bytes):
        row_hex = ""
        row_asc = ""

        for o in range(0, width):
            v = bytes[offset + o] if offset + o < len(bytes) else None

            if v is None:
                row_hex += "   "
            else:
                c = chr(v)
                row_hex += f"{v:02X} "
                row_asc += c if c in PRINTABLE else "."

        lines.append(f"{offset:04X}h: {row_hex} | {row_asc}")

        offset += width

    return lines


def dump_ascii_only(bytes: list[int], width: int = 16) -> list[str]:
    lines = []
    offset = 0

    while offset < len(bytes):
        row_asc = ""

        for o in range(0, width):
            v = bytes[offset + o] if offset + o < len(bytes) else None

            if v is not None:
                c = chr(v)
                row_asc += c if c in PRINTABLE else "."

        lines.append(row_asc)

        offset += width

    return lines
