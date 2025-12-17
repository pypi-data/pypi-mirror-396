import argparse
import os
from pathlib import Path

from . import logger
from .graph import AnsibleGraph

DEFAULT_OUTPUT_PATH = Path(os.getcwd(), "ansible_graph.png")
DEFAULT_ROLES_DIR = Path(os.getcwd(), "roles")


def handle_playbook(args):
    g = AnsibleGraph(Path(args.roles_dir))
    fname = args.file_name
    output_path = Path(args.output_path)

    logger.info(f"Analyzing playbook {fname}")
    g.analyze_playbook(Path(fname))

    logger.info(f"Saving graph output to {output_path}")
    g.write_graph("png", output_path)


def handle_all(args):
    g = AnsibleGraph(Path(args.roles_dir))
    output_path = Path(args.output_path)
    directory = Path(args.directory)
    if not directory.is_dir():
        raise ValueError(f"{directory} is not a directory!")

    logger.info(f"Analyzing all playbooks under {directory}")
    g.analyze_all(directory)

    logger.info(f"Saving graph output to {output_path}")
    g.write_graph("png", output_path)


def main():
    shared_parser = argparse.ArgumentParser(add_help=False)

    shared_parser.add_argument(
        "-r",
        "--roles-dir",
        default=DEFAULT_ROLES_DIR,
        help="directory to load roles from",
    )
    shared_parser.add_argument(
        "-o", "--output-path", default=DEFAULT_OUTPUT_PATH, help="playbook path"
    )

    root_parser = argparse.ArgumentParser(prog="ansible-analyzer")
    subparsers = root_parser.add_subparsers(required=True)

    playbook_parser = subparsers.add_parser(
        name="playbook",
        aliases=["p"],
        help="Parse a specific playbook file",
        parents=[shared_parser],
    )
    playbook_parser.add_argument(
        "-f", "--file-name", required=False, help="playbook file path"
    )
    playbook_parser.set_defaults(func=handle_playbook)

    all_parser = subparsers.add_parser(
        name="all",
        aliases=["a"],
        help="Parse all playbooks and print global stats",
        parents=[shared_parser],
    )
    all_parser.add_argument("-d", "--directory", required=True)
    all_parser.set_defaults(func=handle_all)

    args = root_parser.parse_args()
    args.func(args)
