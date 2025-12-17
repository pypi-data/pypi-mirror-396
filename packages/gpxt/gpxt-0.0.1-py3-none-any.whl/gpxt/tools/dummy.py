import argparse
import logging

from ._tool_descriptor import Tool


def main(gpx_file: str) -> bool:
    logging.info(f"Dummy tool, {gpx_file} file provided")
    return True



def add_argparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "dummy",
        help="Dummy tool."
    )
    parser.add_argument(
        "gpx_file",
        help="Path to the gpx file."
    )

tool = Tool(
    name="dummy",
    description="Dummy tool.",
    add_argparser=add_argparser,
    main=main
)
