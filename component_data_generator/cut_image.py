# coding: utf-8

import argparse
import math
from pathlib import Path
from typing import Sequence

import tqdm
from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # Reference: https://stackoverflow.com/a/51152514


def arg_parser() -> argparse.Namespace:
    """取得執行程式時傳遞的參數

    tutorial: https://docs.python.org/zh-tw/3/howto/argparse.html#
    reference: https://docs.python.org/zh-tw/3/library/argparse.html#nargs

    Returns:
        argparse.Namespace: 使用args.name取得傳遞的參數
    """

    parser = argparse.ArgumentParser(description="Cut image")
    parser.add_argument("-i", "--input_image_path", required=True, help="Image path, can be folder")
    parser.add_argument("-o", "--output_dir", required=True, help="Output folder path")
    parser.add_argument(
        "-s",
        "--image_size",
        type=int,
        nargs="+",
        default=(640, 640),
        help="Cut image size, input like `-s 320 320` mean `320x320`",
    )
    parser.add_argument("--add_prefix", action="store_true", help="Cut image name add prefix from filename")

    args = parser.parse_args()

    return args


def cut(
    image: Image,
    output_dir: str,
    image_size: Sequence,
    add_prefix: bool = False,
    prefix: str = "",
) -> None:
    all_y = [n for n in range(1, math.ceil(image.height / image_size[1]) + 1)]
    all_x = [n for n in range(1, math.ceil(image.width / image_size[0]) + 1)]

    with tqdm.tqdm(total=len(all_x) * len(all_y)) as progress_bar:
        for y in all_y:
            for x in all_x:
                cut_diagram_image = image.crop(
                    (
                        (x - 1) * image_size[0],
                        (y - 1) * image_size[1],
                        min([x * image_size[0], image.width]),
                        min([y * image_size[1], image.height]),
                    )
                )

                filename = f"{x}_{y}.png"
                filename = f"{prefix}_{filename}" if add_prefix else filename
                cut_diagram_image.save(str(Path(output_dir, filename)))
                progress_bar.update()


def main(
    input_image_path: str,
    output_dir: str,
    image_size: Sequence,
    **kwds,
):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    image_path = Path(input_image_path)
    if image_path.is_dir():
        for filename in image_path.iterdir():
            if filename.suffix not in [".png", ".jpg", ".jpeg"]:
                continue
            _output_path = Path(output_path, filename.stem)
            _output_path.mkdir(parents=True, exist_ok=True)
            cut(
                image=Image.open(str(filename)),
                output_dir=str(_output_path),
                image_size=image_size,
                prefix=filename.stem,
                **kwds,
            )
    else:
        cut(
            image=Image.open(str(image_path)),
            output_dir=str(output_path),
            image_size=image_size,
            prefix=image_path.stem,
            **kwds,
        )


if __name__ == "__main__":
    arg = arg_parser()
    main(**vars(arg))
