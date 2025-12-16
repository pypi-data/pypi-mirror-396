import re
from collections.abc import Iterator
from re import Pattern

from supertape.core.basic.opcodes import OPCODES


def remove_spaces(program: str) -> str:
    in_string: bool = False

    target: str = ""

    for c in program:
        if c == '"':
            in_string = not in_string

        if c == " " and not in_string:
            continue

        target += c

    return target


def variable_name_generator(blacklist: list[str]) -> Iterator[str]:
    # c1 does not include I or T to avoid generation of an IF or TO variable name
    # that would collide with BASIC keywords
    for c1 in " ABCDEFGHJKLMNOPQRSUVWXYZ":
        for c2 in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            vname = c1.strip() + c2

            if vname in blacklist:
                continue

            yield vname


def extract_variable_names(program: str) -> set[str]:
    # Remove keywords, literals remarks
    ix: int = 0
    target: str = ""

    while ix < len(program):
        c = program[ix]
        if c == '"':
            ix = program.index('"', ix + 1) + 1
            target += " "
            continue

        if program[ix : ix + 3] == "REM":
            ix = program.index("\n", ix)
            target += " "
            continue

        opc: bool = False

        for kw in OPCODES.values():
            if program[ix : ix + len(kw)] == kw:
                ix += len(kw)
                target += " "
                opc = True
                break

        if opc:
            continue

        target += c
        ix += 1

    re_vars: Pattern[str] = re.compile(r"[^A-Z]([A-Z]+)")
    variables: set[str] = set(re_vars.findall(target))
    return variables


def shorten_variables(program: str) -> str:
    variables: list[str] = list(extract_variable_names(program))

    gen: Iterator[str] = variable_name_generator(variables)

    # Sort variables by length descending to avoid substring
    # matching if names overlap (like var LONG and var LONGER).
    variables.sort(key=len, reverse=True)

    for var in variables:
        substitution: str = gen.__next__()

        if len(var) <= len(substitution):
            continue

        processed: int = 0

        while True:
            ix: int = program.find(var, processed)

            if ix == -1:
                break

            # Skip strings - count quotes to end of line, if odd, then we are in a string
            quotes: int = 0
            ti: int = ix + 1
            while program[ti] != "\n":
                if program[ti] == '"':
                    quotes += 1
                ti += 1

            if quotes % 2 == 1:
                processed = ix + 1
                continue

            clashing_keywords: list[str] = [k for k in OPCODES.values() if var in k]

            clashing: bool = False

            for kw in clashing_keywords:
                kwl: int = len(kw)
                for kwoffs in range(kwl):
                    if program[ix - kwoffs : ix - kwoffs + kwl] == kw:
                        clashing = True

            processed = ix + len(substitution)

            if clashing:
                continue

            program = program[:ix] + substitution + program[ix + len(var) :]

    return program


def minify_basic(program: str) -> str:
    program = remove_spaces(program)
    program = shorten_variables(program)
    return program
