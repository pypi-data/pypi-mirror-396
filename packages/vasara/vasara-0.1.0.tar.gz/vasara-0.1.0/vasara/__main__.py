#!/bin/python3
import concurrent.futures
import json
from argparse import ArgumentParser

import requests
import wikitextparser as wtp

NAME = "Vasara"
DESCRIPTION = "A fun little command-line tool for fetching random Warhammer lore snippets from the wiki."

URLS = {
    "40k": "https://warhammer40k.fandom.com/api.php",
    "fantasy": "https://warhammerfantasy.fandom.com/api.php",
    "aos": "https://ageofsigmar.fandom.com/api.php",
}

WORD_BLACKLIST = {
    "games workshop",
    "fantasy flight",
    "computer game",
    "video game",
    "miniature",
    "tabletop",
    "wargame",
    "novel",
    "short story",
    "anthology",
    "role-playing",
    "author ",
    "-page ",
    "hardback",
    "softcover",
    "author",
    "this page",
    "in progress",
    "please see ",
}


def is_valid_lore(lore: str):
    # If first character is in lowercase, we assume something went wrong with the parsing
    if not lore or not lore[0].isalpha() or lore[0].islower():
        return False
    if [w for w in WORD_BLACKLIST if w in lore.lower()]:
        return False
    return True


def clean_wikitext(text: str):
    return "\n".join(
        [
            line
            for line in text.splitlines()
            if not line.lower().startswith("category:") and not line.startswith("=")
        ]
    )


def get_snippet(text: str, full_paragraph: bool):
    if full_paragraph or len(text) < 180:
        return text

    snippet_end = 0
    while snippet_end < 180:
        new_end = text.find(". ", snippet_end)
        if new_end < 0:
            break
        snippet_end = new_end + 1
    return text if snippet_end < 1 else text[:snippet_end]


def get_lore(url, retry_count, full_paragraph=False):
    for _ in range(retry_count):
        res = requests.get(
            url,
            params={
                "action": "query",
                "format": "json",
                "generator": "random",
                "grnnamespace": "0",
                "prop": "revisions",
                "rvprop": "content",
                "rvslots": "*",
            },
        )

        res.raise_for_status()

        data = res.json()
        page_id = list(data["query"]["pages"].keys())[0]
        text = data["query"]["pages"][page_id]["revisions"][0]["slots"]["main"]["*"]
        parsed = clean_wikitext(wtp.parse(text).plain_text().strip())

        result = parsed.split("\n\n")[0]
        result.replace("\n", " ").strip()
        result.replace("  ", " ")
        result.replace("’", "'")

        lore = get_snippet(result, full_paragraph).replace("\n", " ")

        if not is_valid_lore(lore):
            continue
        return lore
    raise Exception(f"Failed to get valid lore in {retry_count} tries.")


def main():
    parser = ArgumentParser("Vasara", description=DESCRIPTION)

    parser.add_argument(
        "universe",
        choices=list(URLS.keys()),
        default="40k",
        nargs="?",
    )
    parser.add_argument("-c", "--count", type=int, default=1)
    parser.add_argument("-p", "--paragraph", action="store_true")
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument(
        "-f", "--format", type=str, choices=["text", "json", "lua"], default="text"
    )
    args = parser.parse_args()

    universe: str = args.universe
    count: int = max(args.count, 1)
    paragraph: bool = args.paragraph
    retries: int = max(args.retries, 0)
    format = args.format

    url = URLS[universe]

    result_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
        futures = []
        for _ in range(count):
            futures.append(executor.submit(get_lore, url, retries, paragraph))
        for future in concurrent.futures.as_completed(futures):
            result_list.append(future.result())

    if format == "json":
        print(json.dumps(result_list, ensure_ascii=False))
    else:
        print("\n".join(result_list))


if __name__ == "__main__":
    main()
