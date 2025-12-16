# Vasara
A fun little command-line tool for fetching random Warhammer lore snippets from the wikis.

## Usage

`vasara` is a command-line tool for fetching random Warhammer lore snippets.

```bash
vasara [universe] [OPTIONS]
```

### Arguments:

*   **`universe`**: The Warhammer universe you want to get lore snippets from.
    *   Choices: `40k`, `fantasy`, `aos`
    *   Default: `40k`

### Options:

*   `-c`, `--count <COUNT>`: Number of lore snippets to fetch.
    *   Default: `1`
*   `-p`, `--paragraph`: Fetch a full paragraph instead of a snippet.
*   `--retries <RETRIES>`: Number of retries to attempt before cancelling.
    *   Default: `5`
*   `-f`, `--format <FORMAT>`: Output format.
    *   Choices: `text`, `json`
    *   Default: `text`

## Examples

Fetch a single Warhammer 40,000 lore snippet (default):

```bash
vasara
```

Fetch 3 Age of Sigmar lore snippets:

```bash
vasara aos --count 3
```

Fetch a full paragraph of Warhammer Fantasy Battles lore:

```bash
vasara fantasy --paragraph
```

Fetch lore in JSON format:

```bash
vasara 40k --count 2 --format json
```
