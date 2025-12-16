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

    # Now patch all labels

    for label, basic_line in labels.items():
        target = re.sub(r"(GOTO|GOSUB)\s*(" + label + ")", r"\1 " + str(basic_line), target)

    return target
