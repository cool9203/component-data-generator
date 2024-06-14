# coding: utf-8

import argparse
from pathlib import Path

import pdf2image
import PIL.Image

PIL.Image.MAX_IMAGE_PIXELS = None  # Reference: https://stackoverflow.com/a/51152514


def arg_parser() -> argparse.Namespace:
    """取得執行程式時傳遞的參數

    tutorial: https://docs.python.org/zh-tw/3/howto/argparse.html#
    reference: https://docs.python.org/zh-tw/3/library/argparse.html#nargs

    Returns:
        argparse.Namespace: 使用args.name取得傳遞的參數
    """

    parser = argparse.ArgumentParser(description="Convert pdf to png.")
    parser.add_argument("-p", "--pdf_path", required=True, help="Pdf path")
    parser.add_argument("-o", "--output_folder", required=True, help="Output folder path")
    parser.add_argument("-d", "--dpi", type=int, default=200, help="Convert pdf dpi")

    args = parser.parse_args()

    return args


def main(
    pdf_path: str,
    output_folder: str,
    dpi: int = 200,
    **kwds,
):
    images = pdf2image.convert_from_path(
        pdf_path=pdf_path,
        dpi=dpi,
    )
    save_root_path = Path(output_folder, Path(pdf_path).stem)
    save_root_path.mkdir(parents=True, exist_ok=True)
    for i, image in enumerate(images):
        image.save(str(Path(save_root_path, f"{str(i + 1)}.png")))


if __name__ == "__main__":
    arg = arg_parser()
    main(**vars(arg))
