import argparse

import imageio.v3 as iio
import numpy as np


class VideoMode:
    def __init__(
        self,
        width: int,
        height: int,
        palette: dict[int, tuple[int, int, int]],
        block_width: int,
        block_height: int,
    ) -> None:
        self.width: int = width
        self.height: int = height
        self.palette: dict[int, tuple[int, int, int]] = palette
        self.block_width: int = block_width
        self.block_height: int = block_height


palette_highcolor: dict[int, tuple[int, int, int]] = {
    0: (0, 0, 0),
    1: (0, 255, 0),
    2: (255, 255, 0),
    3: (0, 0, 255),
    4: (255, 0, 0),
    5: (255, 255, 255),
    6: (0, 255, 255),
    7: (255, 0, 255),
    8: (255, 128, 0),
}

palette_lowcolor: dict[int, tuple[int, int, int]] = {0: (0, 0, 0), 1: (0, 255, 0), 2: (255, 255, 255)}

alice_modes: dict[int, VideoMode] = {
    32: VideoMode(64, 32, palette_highcolor, 2, 2),
    40: VideoMode(80, 50, palette_highcolor, 2, 2),
    80: VideoMode(160, 100, palette_lowcolor, 2, 5),
    81: VideoMode(160, 100, palette_lowcolor, 2, 5),
}


def compute_gap(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> int:
    gap = abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2])
    return gap


def patterns(block_shape: tuple[int, int, int], color_index: int) -> np.ndarray:
    pixels_count: int = block_shape[0] * block_shape[1]
    result: np.ndarray = np.empty((0, block_shape[0], block_shape[1]))

    i: int
    for i in range(pow(2, pixels_count)):
        block: np.ndarray = np.array(
            [color_index if i & (1 << x) != 0 else 0 for x in range(pixels_count)]
        ).reshape(1, block_shape[0], block_shape[1])
        result = np.vstack((result, block))

    return result


def closest_colors_flat(block_rgb: np.ndarray, palette: dict[int, tuple[int, int, int]]) -> np.ndarray:
    closest_pattern: np.ndarray | None = None
    closest_gap: int = 1024 * 1024

    cix: int
    _cval: tuple[int, int, int]
    for cix, _cval in palette.items():
        pattern: np.ndarray
        for pattern in patterns(block_rgb.shape, cix):
            gap: int = 0

            for paty in range(pattern.shape[0]):
                for patx in range(pattern.shape[1]):
                    gap += compute_gap(block_rgb[paty][patx], palette[pattern[paty][patx]])

            if gap < closest_gap:
                closest_pattern = pattern
                closest_gap = gap

    if closest_pattern is None:
        # Return a default pattern if no match found
        return np.zeros((block_rgb.shape[0], block_rgb.shape[1]), dtype=np.int32)
    return closest_pattern


def closest_colors_biased(
    block_rgb: np.ndarray, palette: dict[int, tuple[int, int, int]], bias: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    closest_pattern: np.ndarray | None = None
    closest_bias: np.ndarray | None = None
    closest_gap: int = 1024 * 1024

    for cix, _cval in palette.items():
        for pattern in patterns(block_rgb.shape, cix):
            gap = bias

            for paty in range(pattern.shape[0]):
                for patx in range(pattern.shape[1]):
                    gap = gap + block_rgb[paty][patx] - palette[pattern[paty][patx]]

            if np.sum(np.absolute(gap)) < closest_gap:
                closest_pattern = pattern
                closest_gap = np.sum(np.absolute(gap))
                closest_bias = gap

    if closest_pattern is None or closest_bias is None:
        # Return default values if no match found
        default_pattern = np.zeros((block_rgb.shape[0], block_rgb.shape[1]), dtype=np.int32)
        default_bias = np.zeros_like(bias)
        return default_pattern, default_bias
    return closest_pattern, closest_bias


def load_and_resize_image(image_file: str, mode: VideoMode) -> np.ndarray:
    img = iio.imread(image_file)
    im_height, im_width, im_depth = img.shape
    buffer = np.zeros((mode.height, mode.width, 3), dtype=np.uint8)

    for y in range(mode.height):
        for x in range(mode.width):
            im_x1 = int(im_width * x / mode.width)
            im_y1 = int(im_height * y / mode.height)
            im_x2 = int(im_width * (x + 1) / mode.width)
            im_y2 = int(im_height * (y + 1) / mode.height)

            total_values = [0, 0, 0]
            samples = 0

            for im_y in range(im_y1, im_y2):
                for im_x in range(im_x1, im_x2):
                    samples += 1
                    for c in range(3):
                        total_values[c] += img[im_y][im_x][c]

            buffer[y][x] = [int(v / samples) for v in total_values]

    return buffer


def generate_image_data_flat(buffer: np.ndarray, mode: VideoMode) -> np.ndarray:
    alice_screen = np.zeros((mode.height, mode.width, 1), dtype=np.uint8)

    for y in range(0, mode.height, mode.block_height):
        for x in range(0, mode.width, mode.block_width):
            image_c = buffer[y : y + mode.block_height, x : x + mode.block_width]
            alice_pattern = closest_colors_flat(image_c, mode.palette)

            for by in range(alice_pattern.shape[0]):
                for bx in range(alice_pattern.shape[1]):
                    alice_screen[y + by][x + bx] = alice_pattern[by][bx]

    return alice_screen


def generate_image_data_dithered(buffer: np.ndarray, mode: VideoMode) -> np.ndarray:
    alice_screen = np.zeros((mode.height, mode.width, 1), dtype=np.uint8)
    bias = np.array([0, 0, 0])

    for y in range(0, mode.height, mode.block_height):
        for x in range(0, mode.width, mode.block_width):
            image_c = buffer[y : y + mode.block_height, x : x + mode.block_width]
            alice_pattern, bias = closest_colors_biased(image_c, mode.palette, bias)

            for by in range(alice_pattern.shape[0]):
                for bx in range(alice_pattern.shape[1]):
                    alice_screen[y + by][x + bx] = alice_pattern[by][bx]

    return alice_screen


def generate_image_data(alice_screen: np.ndarray, mode: VideoMode) -> list[int]:
    data = []
    current_l = 0
    current_c = None
    for y in range(mode.height):
        for x in range(mode.width):
            alice_c = alice_screen[y][x][0]

            if alice_c == current_c:
                current_l += 1
            else:
                if current_c is not None:
                    data += [current_c, current_l]

                current_l = 1
                current_c = alice_c

    data += [current_c, current_l, 0, 0]

    return data


reader_program = """
       CLS0
       X=0:Y=0:C=0
LOOP:  READ C
       READ L
       IF L=0 THEN END
       FOR I=1 TO L
       IF C>0 THEN SET(X,Y,C)
       X=X+1
       IF X=%d THEN X=0:Y=Y+1
       NEXT I
       GOTO LOOP

"""


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Convert an image file to a basic program."
    )
    parser.add_argument("--mode", help="Screen mode to target: 32, 40 or 80", type=int, default=40)
    parser.add_argument("--dithering", help="Set dithering true/false", type=bool, default=False)
    parser.add_argument("image_file", help="Image file to load", type=str)
    args: argparse.Namespace = parser.parse_args()

    display_mode: VideoMode = alice_modes[args.mode]

    buffer: np.ndarray = load_and_resize_image(args.image_file, display_mode)

    alice_screen: np.ndarray = (
        generate_image_data_dithered(buffer, display_mode)
        if args.dithering
        else generate_image_data_flat(buffer, display_mode)
    )

    image_data: list[int] = generate_image_data(alice_screen, display_mode)

    print(reader_program % display_mode.width, end="")

    while image_data:
        chunk: list[int] = image_data[:12]
        image_data = image_data[len(chunk) :]

        line: str = "       DATA "

        i: int
        v: int
        for i, v in enumerate(chunk):
            line += str(v)
            if i < len(chunk) - 1:
                line += ","

        print(line)


if __name__ == "__main__":
    main()
