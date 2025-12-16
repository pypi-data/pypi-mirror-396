import argparse
from typing import TextIO

from supertape.core.basic.minification import minify_basic
from supertape.core.basic.preprocess import preprocess_basic


def read_program(file: str) -> str:
    f: TextIO
    with open(file) as f:
        basic_source: str = f.read()

    return basic_source


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Pre-process a BASIC file.")
    parser.add_argument("--minify", help="Minify the target program.", action="store_true")
    parser.add_argument("file", help="The BASIC code to pre-process", type=str)
    args: argparse.Namespace = parser.parse_args()

    basic_code: str = read_program(args.file)
    basic_code = preprocess_basic(basic_code)

    if args.minify:
        basic_code = minify_basic(basic_code)

    print(basic_code)


if __name__ == "__main__":
    main()
