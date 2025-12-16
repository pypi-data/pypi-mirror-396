#!/bin/python3
import json
from argparse import ArgumentParser

from .core import Config, fetch_random_lore


def main():
    parser = ArgumentParser("Vasara", description=Config.DESCRIPTION)

    parser.add_argument(
        "universe",
        choices=list(Config.URLS.keys()),
        default="40k",
        nargs="?",
    )
    parser.add_argument("-c", "--count", type=int, default=1)
    parser.add_argument("-p", "--paragraph", action="store_true")
    parser.add_argument("-m", "--max-length", type=int, default=Config.MAX_LENGTH)
    parser.add_argument(
        "-f", "--format", type=str, choices=["text", "json"], default="text"
    )
    parser.add_argument("--retries", type=int, default=Config.RETRIES)
    parser.add_argument("--max-workers", type=int, default=Config.MAX_WORKERS)
    args = parser.parse_args()

    universe: str = args.universe
    count: int = max(args.count, 1)
    full_paragraph: bool = args.paragraph
    max_length: int = max(args.max_length, 1)
    retries: int = max(args.retries, 0)
    format: str = args.format
    max_workers: int = max(args.max_workers, 1)

    result_list = fetch_random_lore(
        universe, count, max_length, full_paragraph, retries, max_workers
    )

    if format == "json":
        print(json.dumps(result_list, ensure_ascii=False))
    else:
        print("\n".join(result_list))


if __name__ == "__main__":
    main()
