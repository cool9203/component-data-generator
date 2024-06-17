# coding: utf-8

import copy
import json
import random
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple, Union
from uuid import uuid4

import imgaug.augmenters as iaa
import matplotlib.pyplot as plt
import numpy as np
import tqdm
from PIL import Image, ImageDraw

import utils

from . import generator, probability
from ._types import (
    ImageType,
    _component_augmentation,
    _component_data_dir_name,
    _image_background,
    _image_size,
    _legend_data_dir_name,
    _line_color,
    _line_width,
    _logger_level,
    _max_iteration,
    _min_component,
    _min_line,
    _normal_variate_mu,
    _normal_variate_sigma,
    _origin_data_dir_name,
    _origin_legend_image_filename,
    _paste_legend_image,
    _probability_seed,
    _rectangle_color,
    _rectangle_use_max,
    _rectangle_width,
    _resize_range,
    _root_path,
    _rotate_angles,
    _seed,
    _tend_to_repeat_component,
)
from .probability import area_probability, base_probability, get_gauss_int
from .util import get_rng

logger = utils.get_logger(
    logger_name=__name__,
    log_level=_logger_level.upper(),
    log_fmt=_logger_level,
)

rng = random.Random(_seed)

# Monkey patch imgaug error
np.bool = np.bool_

ComponentData = List[Dict[str, Union[str, ImageType]]]

_image_suffixes = [
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
]

# augmentation_seq = iaa.SomeOf(
#     1,
#     [
#         iaa.GaussianBlur(sigma=(0.0, 4.0)),  # 高斯模糊
#         iaa.MultiplyAndAddToBrightness(mul=(0.5, 1.5), add=(-40, 40)),  # 直接增加RGB數值或乘上倍數
#         # Reference: https://github.com/aleju/imgaug?tab=readme-ov-file#example_images
#     ],
# )

augmentation_seq = iaa.Sequential(
    [
        iaa.RandAugment(n=2, m=9),
    ]
)


def is_debug():
    return _logger_level == "DEBUG"


def seed(seed):
    global rng
    rng = get_rng(seed)


def load_component_data(
    root_path: Path,
    component_data_dir_name: str,
    component_name_merge: bool,
) -> ComponentData:
    components = list()
    for filename in (root_path / component_data_dir_name).iterdir():
        processed_filename = filename.name
        non_rotate = False

        for suffix in filename.suffixes:
            if suffix.lower() in _image_suffixes:
                processed_filename = processed_filename.replace(suffix, "")

            if suffix.lower() in [".nr", ".nonrotate"]:
                non_rotate = True
                processed_filename = processed_filename.replace(suffix, "")

        if component_name_merge:
            for suffix in filename.suffixes:
                processed_filename = processed_filename.replace(suffix, "")
        processed_filename = processed_filename.replace("_", " ").replace("-", " ")
        components.append(
            {
                "image": Image.open(str(filename)),
                "name": processed_filename,
                "non-rotate": non_rotate,
            }
        )
    return components


def load_image_data(path: Path) -> List[ImageType]:
    images = list()
    if isinstance(path, (str, Path)):
        path = Path(path)
        if path.exists():
            if path.is_dir():
                for filename in path.iterdir():
                    images.append(Image.open(str(filename)))
            else:
                images.append(Image.open(str(path)))
        else:
            raise FileNotFoundError(f"image_background: `{path}` not exists")
    return images


def _check_overlap(
    a: Tuple[int, int, int, int],
    b: Tuple[int, int, int, int],
) -> bool:
    """Algorithm reference from: https://stackoverflow.com/a/306332

    Args:
        a (Tuple[int, int, int, int]): _description_
        b (Tuple[int, int, int, int]): _description_

    Returns:
        bool: _description_
    """
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def generate(
    min_component: int = _min_component,
    min_line: int = _min_line,
    root_path: Union[str, Path] = _root_path,
    component_data_dir_name: str = _component_data_dir_name,
    origin_data_dir_name: str = _origin_data_dir_name,
    origin_legend_image_filename: str = _origin_legend_image_filename,
    image_size: Tuple[int, int] = _image_size,
    image_background: Union[str, Tuple[int, int, int]] = _image_background,
    line_color: Tuple[int, int, int] = _line_color,
    line_width: float = _line_width,
    rectangle_color: Tuple[int, int, int] = _rectangle_color,
    rectangle_width: float = _rectangle_width,
    angles: Sequence = _rotate_angles,
    max_iteration: int = _max_iteration,
    normal_variate_mu: int = _normal_variate_mu,
    normal_variate_sigma: int = _normal_variate_sigma,
    paste_legend_image: bool = _paste_legend_image,
    tend_to_repeat_component: bool = _tend_to_repeat_component,
    resize_range: Sequence = _resize_range,
    component_augmentation: bool = _component_augmentation,
    rectangle_use_max: bool = _rectangle_use_max,
    components: ComponentData = None,
    legend_image: ImageType = None,
    background_images: List[ImageType] = None,
    **kwds,
) -> Tuple[ImageType, Dict[str, Any]]:
    start_time = time.time()

    # Try Load background_images
    if not background_images:
        background_images = load_image_data(image_background)

    # Get base_image
    if background_images:
        random_background_image_index = rng.randint(0, len(background_images) - 1)
        base_image = copy.deepcopy(background_images[random_background_image_index])
        if base_image.size != image_size:
            base_image = base_image.resize(size=image_size)
    else:
        base_image = Image.new(mode="RGB", size=image_size, color=image_background)

    boundary_x = image_size[0]
    boundary_y = image_size[1]

    if paste_legend_image:
        if not legend_image:
            legend_image = Image.open(str(root_path / origin_data_dir_name / origin_legend_image_filename))

        base_image.paste(
            legend_image,
            box=(
                image_size[0] - legend_image.width,
                image_size[1] - legend_image.height,
            ),
        )

        boundary_x -= legend_image.width

    gauss_params = {
        "mu": normal_variate_mu,
        "sigma": normal_variate_sigma,
    }

    if rectangle_use_max:
        rectangle_area = ((0, 0), image_size)
    else:
        rectangle_area = (
            (get_gauss_int(0, boundary_x // 2, **gauss_params), get_gauss_int(0, boundary_y // 2, **gauss_params)),
            (
                get_gauss_int(boundary_x // 2, boundary_x, **gauss_params),
                get_gauss_int(boundary_y // 2, boundary_y, **gauss_params),
            ),
        )
    base_image_draw = ImageDraw.ImageDraw(base_image)

    logger.debug(f"rectangle_area: {rectangle_area}")

    # if is_debug():
    #     plt.imshow(base_image)
    #     plt.show()

    if not components:
        components = load_component_data(
            root_path=root_path,
            component_data_dir_name=component_data_dir_name,
        )
    draw_params = list()
    used_component_position = list()
    max_area = (rectangle_area[1][0] - rectangle_area[0][0]) * (rectangle_area[1][1] - rectangle_area[0][1])
    used_area = 0
    components_quantity = {components[i]["name"]: 0 for i in range(len(components))}
    components_detail = list()
    iteration_count = 0

    _pre_index = None
    # Draw component
    while (
        len(used_component_position) < min_component or area_probability(used_area, max_area)
    ) and iteration_count < max_iteration:
        iteration_count += 1
        (x, y) = (
            abs(rng.randint(rectangle_area[0][0], rectangle_area[1][0])),
            abs(rng.randint(rectangle_area[0][1], rectangle_area[1][1])),
        )
        index = (
            _pre_index
            if tend_to_repeat_component and _pre_index and rng.random() > (1 / len(components))
            else rng.randint(0, len(components) - 1)
        )
        select_component = copy.deepcopy(components[index])
        resize_multiple = rng.uniform(resize_range[0], resize_range[1])

        processed_component = select_component["image"]

        # Image augmentation
        if component_augmentation:
            processed_component = augmentation_seq(image=np.asarray(processed_component))
            processed_component = Image.fromarray(processed_component)

        # Resize component
        processed_component = processed_component.resize(
            (
                int(select_component["image"].width * resize_multiple),
                int(select_component["image"].height * resize_multiple),
            )
        )
        # Rotate component
        if not select_component.get("non-rotate", False):
            processed_component = processed_component.rotate(angles[rng.randint(0, len(angles) - 1)], expand=True)

        position = (x, y, x + processed_component.width, y + processed_component.height)
        if position[2] > rectangle_area[1][0] or position[3] > rectangle_area[1][1]:
            select_component["image"].close()
            processed_component.close()
            continue
        _pre_index = index
        logger.debug(f"lt_x: {position[0]}, lt_y: {position[1]}")
        logger.debug(f"rb_x: {position[2]}, rb_y: {position[3]}")
        if (
            sum(
                [
                    _check_overlap(
                        position,
                        used_component_position[i],
                    )
                    for i in range(len(used_component_position))
                ]
            )
            == 0
        ):
            logger.debug(f"count: {len(used_component_position)}\tSpend time: {time.time() - start_time}")
            iteration_count = 0

            # Record use component
            components_quantity[select_component["name"]] += 1
            used_area += processed_component.width * processed_component.height
            used_component_position.append(position)
            components_detail.append(
                {
                    "component_name": select_component["name"],
                    "position": [x, y, processed_component.width, processed_component.height],
                }
            )
            draw_params.append(
                {
                    "function": base_image.paste,
                    "params": {"im": processed_component, "box": (x, y)},
                    "close_data": [processed_component, select_component["image"]],
                }
            )
            base_image_draw.rectangle(
                xy=(position[0:2], position[2:]),
                fill=None,
                outline=rectangle_color,
                width=rectangle_width,
            ) if is_debug() else None
        logger.debug("-" * 30)

    # Draw line
    used_line_position = list()
    iteration_count = 0
    while (len(used_line_position) < min_line or base_probability()) and iteration_count < max_iteration:
        iteration_count += 1
        index_1 = rng.randint(0, len(used_component_position) - 1)
        index_2 = rng.randint(0, len(used_component_position) - 1)
        if index_1 == index_2:
            continue

        position = (
            (used_component_position[index_1][0] + used_component_position[index_1][2]) / 2,
            (used_component_position[index_1][1] + used_component_position[index_1][3]) / 2,
            (used_component_position[index_2][0] + used_component_position[index_2][2]) / 2,
            (used_component_position[index_2][1] + used_component_position[index_2][3]) / 2,
        )

        if position[2] > rectangle_area[1][0] or position[3] > rectangle_area[1][1] or position in used_line_position:
            continue

        logger.debug(f"lt_x: {position[0]}, lt_y: {position[1]}")
        logger.debug(f"rb_x: {position[2]}, rb_y: {position[3]}")
        used_line_position.append(position)
        draw_params.insert(
            0,
            {
                "function": base_image_draw.line,
                "params": {
                    "xy": position,
                    "fill": line_color,
                    "width": line_width,
                },
            },
        )
        iteration_count = 0
        logger.debug("-" * 30)

    # Draw to base_image
    for i in range(len(draw_params)):
        func = draw_params[i]["function"]
        params = draw_params[i]["params"]
        close_data = draw_params[i].get("close_data", [])
        func(**params)

        for fp in close_data:
            fp.close()

    base_image_draw.rectangle(rectangle_area, fill=None, outline=rectangle_color, width=rectangle_width)

    if is_debug():
        plt.imshow(base_image)
        plt.show()

    return (
        base_image,
        {
            "components_quantity": components_quantity,
            "components_detail": components_detail,
        },
    )


def run_generate(
    output_path,
    **kwds,
) -> bool:
    try:
        (image, config) = generate(**kwds)
        filename = str(uuid4())
        image.save(Path(output_path, f"{filename}.png"))
        image.close()

        with Path(output_path, f"{filename}.json").open(mode="w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        return True
    except Exception:
        return False


def main(**kwds: Dict[str, Any]) -> None:
    output_path = Path(kwds["output_path"])
    output_path.mkdir(parents=True, exist_ok=True)
    del kwds["output_path"]

    # Set seed
    if kwds["seed"] != _seed:
        generator.seed(kwds["seed"])
    if kwds["probability_seed"] != _probability_seed:
        probability.seed(kwds["probability_seed"])

    # Load background
    background_images = load_image_data(kwds["image_background"])

    # Load components
    components = load_component_data(
        root_path=Path(kwds["root_path"]).absolute(),
        component_data_dir_name=kwds["component_data_dir_name"],
        component_name_merge=kwds["component_name_merge"],
    )
    component_names = {component["name"] for component in components}
    logger.info(f"all components count: {len(components)}")
    logger.info(f"all component names count: {len(component_names)}")

    legend_image = Image.open(str(Path(kwds["root_path"]) / kwds["origin_data_dir_name"] / kwds["origin_legend_image_filename"]))

    if "tqdm" in kwds and kwds["tqdm"]:
        with tqdm.tqdm(total=kwds["count"]) as progress_bar:
            i = 0
            while i < kwds["count"]:
                result = run_generate(
                    components=components,
                    legend_image=legend_image,
                    background_images=background_images,
                    output_path=output_path,
                    **kwds,
                )
                if result:
                    progress_bar.update()
                    i += 1
    else:
        i = 0
        while i < kwds["count"]:
            result = run_generate(
                components=components,
                legend_image=legend_image,
                background_images=background_images,
                output_path=output_path,
                **kwds,
            )
            if result:
                i += 1


if __name__ == "__main__":
    main(
        **{
            # Path setting
            "root_path": _root_path,
            "output_path": "./data/output",
            "legend_data_dir_name": _legend_data_dir_name,
            "component_data_dir_name": _component_data_dir_name,
            "origin_data_dir_name": _origin_data_dir_name,
            "origin_legend_image_filename": _origin_legend_image_filename,
            # Image setting
            "image_size": _image_size,
            "image_background": _image_background,
            "rectangle_width": _rectangle_width,
            "rectangle_color": _rectangle_color,
            "line_width": _line_width,
            "line_color": _line_color,
            "rotate_angles": _rotate_angles,
            # Normal setting
            "seed": _seed,
            "probability_seed": _probability_seed,
            "normal_variate_mu": _normal_variate_mu,
            "normal_variate_sigma": _normal_variate_sigma,
            "min_component": _min_component,
            "min_line": _min_line,
            "count": 200000,
            "paste_legend_image": _paste_legend_image,
            "tend_to_repeat_component": _tend_to_repeat_component,
        }
    )
