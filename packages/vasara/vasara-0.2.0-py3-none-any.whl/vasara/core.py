import concurrent.futures

import requests
import wikitextparser as wtp


class Config:
    NAME = "Vasara"
    DESCRIPTION = "A fun little command-line tool for fetching random Warhammer lore snippets from the wiki."

    MIN_LENGTH = 10
    MAX_LENGTH = 190

    MAX_WORKERS = 500
    RETRIES = 5

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
        "art book",
        "author",
        "this article",
        "this page",
        "in progress",
        "please see ",
    }


def is_valid_lore(lore: str, max_length=Config.MAX_LENGTH, full_paragraph=False):
    # Check for length errors, parsing issues and blacklisted words
    if (
        not lore
        or lore[0].islower()
        or not lore[0].isalpha()
        or len(lore) < Config.MIN_LENGTH
        or (not full_paragraph and len(lore) > max_length)
        or [w for w in Config.WORD_BLACKLIST if w in lore.lower()]
    ):
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


def get_snippet(text: str, max_length=Config.MAX_LENGTH, full_paragraph=False):
    snippet_end = text[:max_length].rfind(". ")
    if full_paragraph or len(text) < max_length or snippet_end < 0:
        return text
    return text[: snippet_end + 1].strip()


def get_lore(
    url,
    max_length=Config.MAX_LENGTH,
    full_paragraph=False,
    retries=Config.RETRIES,
):
    for _ in range(retries):
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

        lore = get_snippet(result, max_length, full_paragraph).replace("\n", " ")

        if not is_valid_lore(lore, max_length, full_paragraph):
            continue
        return lore
    msg = f"Failed to get valid lore in {retries} tries."
    raise Exception(msg)


def fetch_random_lore(
    universe: str,
    count=1,
    max_length=Config.MAX_LENGTH,
    full_paragraph=False,
    retries=Config.RETRIES,
    max_workers=Config.MAX_WORKERS,
):
    if not Config.URLS.get(universe):
        msg = f"Invalid universe '{universe}' provided. Accepted values are ({", ".join(list(Config.URLS.keys()))})"
        raise Exception(msg)
    url = Config.URLS[universe]
    result_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for _ in range(count):
            futures.append(
                executor.submit(get_lore, url, max_length, full_paragraph, retries)
            )
        for future in concurrent.futures.as_completed(futures):
            result_list.append(future.result())
    return result_list
