# coding: utf-8

import argparse
from pathlib import Path
from typing import Dict, List

from PIL import Image


def arg_parser() -> argparse.Namespace:
    """取得執行程式時傳遞的參數

    tutorial: https://docs.python.org/zh-tw/3/howto/argparse.html#
    reference: https://docs.python.org/zh-tw/3/library/argparse.html#nargs

    Returns:
        argparse.Namespace: 使用args.name取得傳遞的參數
    """

    parser = argparse.ArgumentParser(description="Combine image")
    parser.add_argument("-i", "--image_path", help="Input folder path")
    parser.add_argument("-o", "--output_path", help="Output filepath")

    args = parser.parse_args()

    return args


def combine_image(
    image_path: str,
    output_path: str = None,
) -> Image.Image:
    image_path: Path = Path(image_path)
    images: Dict[Dict[Image.Image]] = dict()
    width = 0
    height = 0

    for filename in image_path.iterdir():
        if filename.suffix not in [".png", ".jpg", ".jpeg"]:
            continue
        image = Image.open(filename)

        # Get new image property
        width = max([width, image.width])
        height = max([height, image.height])

        filename_split = filename.stem.split("_") if "_" in filename.stem else filename.stem.split("-")
        if len(filename_split) == 2:
            row = int(filename_split[0])
            col = int(filename_split[1])
        elif len(filename_split) == 3:
            row = int(filename_split[1])
            col = int(filename_split[2])
        else:
            raise ValueError("filename need be like `row_col.png`")
        if row not in images:
            images[row] = dict()
        images[row][col] = image

    rows = sorted(list(images.keys()))
    cols = max([len(images[i]) for i in rows])
    start_index = min(rows)

    combined_image = Image.new("RGB", (width * len(rows), height * cols))
    for row in rows:
        for col in sorted(list(images[row].keys())):
            combined_image.paste(
                images[row][col],
                ((row - start_index) * width, (col - start_index) * height),
            )

    if output_path:
        combined_image.save(str(output_path))
    return combined_image


if __name__ == "__main__":
    args = arg_parser()
    combine_image(**vars(args))
