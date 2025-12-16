import re
from re import Pattern

re_comment: Pattern[str] = re.compile(r"^#")
re_white_line: Pattern[str] = re.compile(r"^$")

re_line_number: Pattern[str] = re.compile(r"^(\d+)\s+")
re_line_label: Pattern[str] = re.compile(r"^(\S*):\s+")
re_valid_label: Pattern[str] = re.compile(r"^[A-Z]+$")


class BasicPreprocessingException(Exception):
    pass


class InvalidLabelError(BasicPreprocessingException):
    def __init__(self, label: str, line: int) -> None:
        self.label: str = label
        self.line: int = line

    def __str__(self) -> str:
        return f'Invalid label "{self.label}" at line {self.line}'


class DuplicateLabelError(BasicPreprocessingException):
    def __init__(self, label: str, line: int) -> None:
        self.label: str = label
        self.line: int = line

    def __str__(self) -> str:
        return f'Duplicate label "{self.label}" at line {self.line}'


def _replace_label_in_line(line: str, label: str, line_number: int, compiled_pattern: Pattern[str]) -> str:
    """Replace GOTO/GOSUB label references in a line, avoiding strings and REM comments.

    Args:
        line: The BASIC line to process
        label: The label to replace
        line_number: The line number to replace it with
        compiled_pattern: Pre-compiled regex pattern for this label

    Returns:
        The line with label references replaced
    """
    # Find REM position (comment starts here and goes to end of line)
    rem_pos = line.find("REM")
    if rem_pos == -1:
        rem_pos = len(line)  # No REM, entire line is code

    # Process only the part before REM
    code_part = line[:rem_pos]
    rem_part = line[rem_pos:]

    # Split by quotes to identify strings
    parts = code_part.split('"')

    # Process parts: even indices are outside strings, odd indices are inside strings
    for i in range(0, len(parts), 2):  # Process only parts outside strings
        # Replace GOTO/GOSUB label references using pre-compiled pattern
        parts[i] = compiled_pattern.sub(r"\1 " + str(line_number), parts[i])

    # Reconstruct the line
    return '"'.join(parts) + rem_part


def preprocess_basic(code: str) -> str:
    target: str = ""
    basic_line_number: int = 0
    labels: dict[str, int] = {}

    for original_line_number, line in enumerate(code.splitlines()):
        line = line.upper().strip()
        if re_comment.match(line) or re_white_line.match(line):
            continue

        # Detect line number or label, these are exclusive

        ln_matches = re_line_number.findall(line)
        lb_matches = re_line_label.findall(line)

        # Log the label

        label: str | None = lb_matches[0] if lb_matches else None
        line = re.sub(re_line_label, "", line) if label else line

        # Update the line number variable accordingly

        if ln_matches:
            basic_line_number = int(ln_matches[0])
        else:
            basic_line_number += 1
            line = f"{basic_line_number} {line}"

        # From here in the loop, basic line number is defined accurately

        if lb_matches and label is not None:
            if label in labels.keys():
                raise DuplicateLabelError(label=label, line=original_line_number + 1)

            if not re_valid_label.match(label):
                raise InvalidLabelError(label=label, line=original_line_number + 1)

            labels[label] = basic_line_number

        target += line + "\n"

    # Now patch all labels - compile patterns once for performance
    # Pre-compile all label patterns (O(n) instead of O(n*m) per line)
    compiled_patterns: dict[str, tuple[int, Pattern[str]]] = {}
    for label, basic_line in labels.items():
        pattern = re.compile(r"(GOTO|GOSUB)\s*(" + re.escape(label) + r")\b")
        compiled_patterns[label] = (basic_line, pattern)

    # Process line by line to avoid strings and REM comments
    result_lines = []
    for line in target.splitlines():
        for label, (basic_line, pattern) in compiled_patterns.items():
            line = _replace_label_in_line(line, label, basic_line, pattern)
        result_lines.append(line)

    return "\n".join(result_lines) + ("\n" if result_lines else "")
