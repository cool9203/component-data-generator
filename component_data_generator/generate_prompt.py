# coding: utf-8

import argparse
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Dict, List

import numpy as np
import tqdm

_components_name_sequence = [
    "main transformer",
    "auxiliary earthing transformer",
    "surge arrester",
    "voltage transformer",
    "circuit breaker",
    "3 position disconnector",
    "hv disconnector",
    "earthing switch",
    "current transformer",
    "high speed earthing switch",
    "isolating link",
    "removable link",
    "reactor",
]


def arg_parser() -> argparse.Namespace:
    """取得執行程式時傳遞的參數

    tutorial: https://docs.python.org/zh-tw/3/howto/argparse.html#
    reference: https://docs.python.org/zh-tw/3/library/argparse.html#nargs
    reference-2: https://stackoverflow.com/a/15753721

    Returns:
        argparse.Namespace: 使用args.name取得傳遞的參數
    """

    parser = argparse.ArgumentParser(description="Generate component layout data.")

    parser.add_argument("-i", "--input_dir", type=str, default="./data/output", help="Input folder path")
    parser.add_argument(
        "-o", "--output_path", type=str, default="./data/config.json", help="Output path, need have filename and extension"
    )
    parser.add_argument("-t", "--target_dir", type=str, required=True, help="LLAVA image target root folder path")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-l", "--linux", action="store_true", help="LLAVA path always use linux path")
    group.add_argument("-w", "--windows", action="store_true", help="LLAVA path always use windows path")

    args = parser.parse_args()

    return args


def main(
    input_dir: str,
    target_dir: str,
    output_path: str,
    **kwds,
):
    all_config_filename = [config_path for config_path in Path(input_dir).iterdir() if config_path.suffix in [".json"]]

    if kwds["linux"]:
        _path_fn = PurePosixPath
    elif kwds["windows"]:
        _path_fn = PureWindowsPath
    else:
        _path_fn = Path

    config = list()
    for config_path in tqdm.tqdm(all_config_filename):
        if config_path.suffix == ".json":
            with Path(input_dir, config_path.name).open("r", encoding="utf8") as f:
                data = json.load(f)

            # Fit old version
            if "components_quantity" in data:
                data = data["components_quantity"]

            all_component_name = list(data.keys()) if not _components_name_sequence else _components_name_sequence
            _id = config_path.stem
            config.append(
                {
                    "id": _id,
                    "image": str(_path_fn(target_dir, f"{_id}.png")),
                    "conversations": [
                        {"from": "human", "value": "<image>\ndescription this image.\n"},
                        {
                            "from": "gpt",
                            "value": (
                                "\n".join(all_component_name)
                                + "\n\n"
                                + "\n".join(
                                    [f"{component_name}: {data[component_name]}" for component_name in all_component_name]
                                )
                            ),
                        },
                    ],
                }
            )

    final_config = list()
    index_list = [_ for _ in range(len(config))]
    np.random.shuffle(index_list)
    for i in index_list:
        final_config.append(config[i])

    with Path(output_path).open("w", encoding="utf-8") as f:
        json.dump(
            obj=final_config,
            fp=f,
            indent=4,
        )


if __name__ == "__main__":
    args = arg_parser()
    main(**vars(args))
