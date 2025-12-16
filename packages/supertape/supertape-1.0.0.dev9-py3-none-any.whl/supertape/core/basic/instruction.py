class BasicBinaryInstruction:
    def __init__(self, bytes: list[int]) -> None:
        self.bytes: list[int] = bytes

    def get_bytes(self) -> list[int]:
        return self.bytes

    def __str__(self) -> str:
        return "Basic Instruction: %s" % ([f"0x{b:02x}" for b in self.bytes])
