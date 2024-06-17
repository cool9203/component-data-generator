# coding: utf-8

import argparse
import shutil
from pathlib import Path
from typing import List, Union

PathType = Union[str, Path]


def arg_parser() -> argparse.Namespace:
    """取得執行程式時傳遞的參數

    tutorial: https://docs.python.org/zh-tw/3/howto/argparse.html#
    reference: https://docs.python.org/zh-tw/3/library/argparse.html#nargs

    Returns:
        argparse.Namespace: 使用args.name取得傳遞的參數
    """

    parser = argparse.ArgumentParser(description="your program description.")
    parser.add_argument("-i", "--input_path", type=str, required=True, help="Input dataset path")
    parser.add_argument("-yolo", "--yolo_path", type=str, required=True, help="YOLO path")
    parser.add_argument("-d", "--dataset_path", type=str, required=True, help="Output dataset path")
    parser.add_argument("--train", type=float, default=0.8, help="train dataset size")
    parser.add_argument("--val", type=float, default=0.1, help="val dataset size")
    parser.add_argument("--test", type=float, default=0.1, help="test dataset size")

    args = parser.parse_args()

    return args


def convert_to_yolo_mit(
    input_path: PathType,
    yolo_path: PathType,
    dataset_path: PathType,
    train: float = 0.8,
    val: float = 0.1,
    test: float = 0.1,
    train_folder_name: str = "train",
    val_folder_name: str = "val",
    test_folder_name: str = "test",
):
    assert int(train + val + test) == 1, "train + val + test need is 1.0"

    input_path = Path(input_path)
    yolo_path = Path(yolo_path)
    dataset_path = Path(dataset_path)

    Path(dataset_path, "images", train_folder_name).mkdir(parents=True, exist_ok=True)
    Path(dataset_path, "images", val_folder_name).mkdir(parents=True, exist_ok=True)
    Path(dataset_path, "images", test_folder_name).mkdir(parents=True, exist_ok=True)

    Path(dataset_path, "labels", train_folder_name).mkdir(parents=True, exist_ok=True)
    Path(dataset_path, "labels", val_folder_name).mkdir(parents=True, exist_ok=True)
    Path(dataset_path, "labels", test_folder_name).mkdir(parents=True, exist_ok=True)

    with Path(yolo_path, "yolo", "config", "dataset", f"{dataset_path.stem}.yaml").open("w", encoding="utf-8") as dataset_config:
        dataset_config.write(
            (
                f"path: {dataset_path.resolve()}\n"
                + f"train: {train_folder_name}\n"
                + f"validation: {val_folder_name}\n"
                + f"test: {test_folder_name}\n"
                + "\n"
                + "auto_download:\n"
            )
        )

    filenames = list({filename.stem for filename in input_path.iterdir()})

    train_dataset = filenames[: int(len(filenames) * train)]
    val_dataset = filenames[int(len(filenames) * train) : int(len(filenames) * (train + val))]
    test_dataset = filenames[int(len(filenames) * (train + val)) : int(len(filenames) * (train + val + test))]

    def __copy_dataset(
        dataset: List[str],
        dataset_type: str,
    ):
        for filename in dataset:
            shutil.copy2(
                src=Path(input_path, f"{filename}.png"),
                dst=Path(dataset_path, "images", dataset_type),
            )
            shutil.copy2(
                src=Path(input_path, f"{filename}.txt"),
                dst=Path(dataset_path, "labels", dataset_type),
            )

    __copy_dataset(dataset=train_dataset, dataset_type=train_folder_name)
    __copy_dataset(dataset=val_dataset, dataset_type=val_folder_name)
    __copy_dataset(dataset=test_dataset, dataset_type=test_folder_name)


if __name__ == "__main__":
    args = arg_parser()
    convert_to_yolo_mit(**vars(args))
