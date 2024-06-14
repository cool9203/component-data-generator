# coding: utf-8

import argparse

from component_data_generator._types import (
    _component_augmentation,
    _component_data_dir_name,
    _component_name_merge,
    _count,
    _image_background_color,
    _image_size,
    _legend_data_dir_name,
    _line_color,
    _line_width,
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
from component_data_generator.generator import main


def arg_parser() -> argparse.Namespace:
    """取得執行程式時傳遞的參數

    tutorial: https://docs.python.org/zh-tw/3/howto/argparse.html#
    reference: https://docs.python.org/zh-tw/3/library/argparse.html#nargs
    reference-2: https://stackoverflow.com/a/15753721

    Returns:
        argparse.Namespace: 使用args.name取得傳遞的參數
    """

    parser = argparse.ArgumentParser(description="Generate component layout data.")

    # Path parameters
    parser.add_argument("-i", "--input_path", type=str, default=None, help="Input path")
    parser.add_argument("-o", "--output_path", type=str, default="./data/output", help="Output path")
    parser.add_argument("--component_data_dir_name", type=str, default=None, help="Input component data dir name")
    parser.add_argument("--legend_data_dir_name", type=str, default=None, help="Input legend data dir name")
    parser.add_argument("--origin_data_dir_name", type=str, default=None, help="Input origin data dir name")
    parser.add_argument("--origin_legend_image_filename", type=str, default=None, help="Input origin legend image filename")

    # Image parameters
    parser.add_argument("--image_size", nargs="+", type=int, default=None, help="Generate image size")
    parser.add_argument("--image_background_color", nargs="+", type=str, default=None, help="Generate image background color")
    parser.add_argument("--rectangle_width", type=int, default=None, help="Generate image draw rectangle width")
    parser.add_argument("--rectangle_color", nargs="+", type=str, default=None, help="Generate image draw rectangle color")
    parser.add_argument("--line_width", type=int, default=None, help="Generate image draw line width")
    parser.add_argument("--line_color", nargs="+", type=str, default=None, help="Generate image draw line color")
    parser.add_argument("--rotate_angles", nargs="+", type=int, default=None, help="Components rotate angles")
    parser.add_argument("--resize_range", nargs="+", type=float, default=None, help="Components resize range")
    parser.add_argument("--rectangle_use_max", action="store_true", help="Generate image rectangle use all image")
    parser.add_argument("--component_augmentation", action="store_true", help="Component image use augmentation")
    parser.add_argument(
        "--component_name_merge",
        action="store_true",
        help="Component image file name merge, only can merge like `filename.1.2.png` to `filename`",
    )

    # Normal parameters
    parser.add_argument("--seed", type=int, default=None, help="generator.py seed")
    parser.add_argument("--probability_seed", type=int, default=None, help="probability.py seed")
    parser.add_argument("--normal_variate_mu", type=float, default=None, help="normalvariate mu value")
    parser.add_argument("--normal_variate_sigma", type=float, default=None, help="normalvariate sigma value")
    parser.add_argument("--min_component", type=int, default=None, help="Generate image min component number")
    parser.add_argument("--min_line", type=int, default=None, help="Generate image min line number")
    parser.add_argument("--paste_legend_image", action="store_true", help="Generate image paste legend image in right side")
    parser.add_argument("--tend_to_repeat_component", action="store_true", help="Generate image tend to repeat component")
    parser.add_argument("-c", "--count", type=int, default=None, help="Generate image count")
    parser.add_argument("--tqdm", action="store_true", help="Use tqdm show process progress")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = arg_parser()

    default_args = {
        # Path setting
        "root_path": _root_path,
        "legend_data_dir_name": _legend_data_dir_name,
        "component_data_dir_name": _component_data_dir_name,
        "origin_data_dir_name": _origin_data_dir_name,
        "origin_legend_image_filename": _origin_legend_image_filename,
        # Image setting
        "image_size": _image_size,
        "image_background_color": _image_background_color,
        "rectangle_width": _rectangle_width,
        "rectangle_color": _rectangle_color,
        "line_width": _line_width,
        "line_color": _line_color,
        "rotate_angles": _rotate_angles,
        "resize_range": _resize_range,
        "rectangle_use_max": _rectangle_use_max,
        "component_augmentation": _component_augmentation,
        "component_name_merge": _component_name_merge,
        # Normal setting
        "seed": _seed,
        "probability_seed": _probability_seed,
        "normal_variate_mu": _normal_variate_mu,
        "normal_variate_sigma": _normal_variate_sigma,
        "min_component": _min_component,
        "min_line": _min_line,
        "count": _count,
        "paste_legend_image": _paste_legend_image,
        "tend_to_repeat_component": _tend_to_repeat_component,
    }

    transform_key = {
        "input_path": "root_path",
    }

    for key, value in vars(args).items():
        _key = key if key not in transform_key else transform_key[key]

        # Check color value
        if _key in [
            "image_background_color",
            "rectangle_color",
            "line_color",
        ]:
            if value and len(value) == 1:
                value = str(value[0])
            elif value and len(value) > 1:
                try:
                    value = tuple([int(v) for v in value])
                except ValueError:
                    raise TypeError("color need be str like ['red', 'green', 'blue'], or RGB number like (255, 255, 255).")

        # Trans list to tuple
        if _key in [
            "image_size",
        ]:
            if value and len(value) == 2:
                value = tuple([int(v) for v in value])
            elif value:
                raise ValueError(f"size need be int of tuple like {_image_size}.")

        if value is not None:
            default_args[_key] = value

    print("Used parameters:")
    for key, value in default_args.items():
        if isinstance(value, str):
            print(f"  |- '{key}': '{value}'")
        else:
            print(f"  |- '{key}': {value}")

    main(**default_args)
