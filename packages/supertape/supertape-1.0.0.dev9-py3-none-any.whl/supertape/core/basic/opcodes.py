OPCODES: dict[int, str] = {
    0x80: "FOR",
    0x81: "GOTO",
    0x82: "GOSUB",
    0x83: "REM",
    0x84: "IF",
    0x85: "DATA",
    0x86: "PRINT",
    0x87: "ON",
    0x88: "INPUT",
    0x89: "END",
    0x8A: "NEXT",
    0x8B: "DIM",
    0x8C: "READ",
    0x8D: "LET",
    0x8E: "RUN",
    0x8F: "RESTORE",
    0x90: "RETURN",
    0x91: "STOP",
    0x92: "POKE",
    0x93: "CONT",
    0x94: "LIST",
    0x95: "CLEAR",
    0x96: "NEW",
    0x97: "CLOAD",
    0x98: "CSAVE",
    0x99: "LLIST",
    0x9A: "LPRINT",
    0x9B: "SET",
    0x9C: "RESET",
    0x9D: "CLS",
    0x9E: "SOUND",
    0x9F: "EXEC",
    0xA0: "SKIPF",
    0xA1: "TAB",
    0xA2: "TO",
    0xA3: "THEN",
    0xA5: "STEP",
    0xA7: "+",
    0xA8: "-",
    0xA9: "*",
    0xAA: "/",
    0xAE: ">",
    0xAF: "=",
    0xB0: "<",
    0xB1: "SGN",
    0xB2: "INT",
    0xB3: "ABS",
    0xB5: "RND",
    0xB6: "SQR",
    0xB7: "LOG",
    0xB9: "SIN",
    0xBA: "COS",
    0xBB: "TAN",
    0xBC: "PEEK",
    0xBD: "LEN",
    0xBE: "STR$",
    0xBF: "VAL",
    0xC0: "ASC",
    0xC1: "CHR$",
    0xC2: "LEFT$",
    0xC3: "RIGHT$",
    0xC4: "MID$",
    0xC5: "POINT",
    0xC7: "INKEY$",
    0xC8: "MEM",
}


def binarize(text: str) -> list[int]:
    bytes: list[int] = []
    tix: int = 0
    in_string: bool = False

    while tix < len(text):
        isopcode: bool = False

        if text[tix] == '"':
            in_string = not in_string

        if not in_string:
            for opk, opv in OPCODES.items():
                if text[tix:].startswith(opv):
                    bytes.append(opk)
                    tix += len(opv)
                    isopcode = True

        if not isopcode:
            bytes.append(ord(text[tix]))
            tix += 1

    bytes.append(0)
    return bytes


def stringify(bytes: list[int]) -> str:
    buffer: str = ""

    for b in bytes:
        if b == 0:
            break
        elif b in OPCODES.keys():
            buffer = buffer + OPCODES[b]
        else:
            buffer = buffer + chr(b)

    return buffer
