# coding: utf-8

import argparse
from typing import List

import utils

logger = utils.get_logger(logger_name=__name__)


def arg_parser() -> argparse.Namespace:
    """取得執行程式時傳遞的參數

    tutorial: https://docs.python.org/zh-tw/3/howto/argparse.html#
    reference: https://docs.python.org/zh-tw/3/library/argparse.html#nargs

    Returns:
        argparse.Namespace: 使用args.name取得傳遞的參數
    """

    parser = argparse.ArgumentParser(description="your program description.")
    parser.add_argument("first_arg", type=str, help="help message")
    parser.add_argument("second_arg", type=str, help="help message")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")

    parser.add_argument("-a", "--arg_name", help="help message")

    args = parser.parse_args()

    return args


def main(args: argparse.Namespace) -> None:
    logger.info("this is template.py")
    pass


if __name__ == "__main__":
    args = arg_parser()
    main(args)
    input("press Enter to continue...")
