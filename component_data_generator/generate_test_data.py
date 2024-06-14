# coding: utf-8

import math
from pathlib import Path
from typing import Tuple

import tqdm
from PIL import Image, ImageDraw

from ._types import (
    ImageType,
    _image_background_color,
    _image_size,
    _origin_data_dir_name,
    _origin_diagram_image_filename,
    _origin_legend_image_filename,
    _rectangle_color,
    _rectangle_width,
    _root_path,
)


def main(
    output_dir: str,
    image_size: Tuple[int, int],
    image_background_color: Tuple[int, int, int],
    root_path: str,
    origin_data_dir_name: str,
    origin_legend_image_filename: str,
    origin_diagram_image_filename: str,
    rectangle_color,
    rectangle_width,
    test_image_size: Tuple[int, int],
    legend_image: ImageType = None,
    diagram_image: ImageType = None,
    **kwds,
):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if not legend_image:
        legend_image = Image.open(str(root_path / origin_data_dir_name / origin_legend_image_filename))
    if not diagram_image:
        diagram_image = Image.open(str(root_path / origin_data_dir_name / origin_diagram_image_filename))

    all_y = [n for n in range(1, math.ceil(diagram_image.height / test_image_size[1]) + 1)]
    all_x = [n for n in range(1, math.ceil(diagram_image.width / test_image_size[0]) + 1)]

    with tqdm.tqdm(total=len(all_x) * len(all_y)) as progress_bar:
        for y in all_y:
            for x in all_x:
                base_image = Image.new(mode="RGB", size=image_size, color=image_background_color)
                base_image_draw = ImageDraw.ImageDraw(base_image)
                base_image.paste(
                    legend_image,
                    box=(
                        image_size[0] - legend_image.width,
                        image_size[1] - legend_image.height,
                    ),
                )

                cut_diagram_image = diagram_image.crop(
                    (
                        (x - 1) * test_image_size[0],
                        (y - 1) * test_image_size[1],
                        min([x * test_image_size[0], diagram_image.width]),
                        min([y * test_image_size[1], diagram_image.height]),
                    )
                )
                index = (450, 750)
                base_image.paste(
                    cut_diagram_image,
                    box=index,
                )
                base_image_draw.rectangle(
                    (index, (index[0] + cut_diagram_image.width, index[1] + cut_diagram_image.height)),
                    fill=None,
                    outline=rectangle_color,
                    width=rectangle_width,
                )

                base_image.save(str(Path(output_dir, f"{x}_{y}.png")))
                progress_bar.update()


if __name__ == "__main__":
    main(
        output_dir="./data/test_data",
        image_size=_image_size,
        image_background_color=_image_background_color,
        root_path=_root_path,
        origin_data_dir_name=_origin_data_dir_name,
        origin_legend_image_filename=_origin_legend_image_filename,
        origin_diagram_image_filename=_origin_diagram_image_filename,
        rectangle_color=_rectangle_color,
        rectangle_width=_rectangle_width,
        test_image_size=(500, 500),
    )
