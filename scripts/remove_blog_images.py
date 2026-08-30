#!/usr/bin/env python3
"""Remove blog image metadata and markup from the complete local portfolio."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_IMAGE = re.compile(r"!\[([^\]]*)\]\([^\n)]*\)")
HTML_IMAGE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)


def image_free_markdown(document: str) -> str:
    """Strip known image frontmatter plus inline image markup idempotently."""
    lines = document.splitlines(keepends=True)
    if lines and lines[0].strip() == "---":
        end = next(
            (index for index, line in enumerate(lines[1:], 1) if line.strip() == "---"),
            None,
        )
        if end is not None:
            cleaned: list[str] = [lines[0]]
            index = 1
            while index < end:
                stripped = lines[index].lstrip()
                if stripped.startswith("coverImage:"):
                    index += 1
                    continue
                if stripped.startswith("ogImage:"):
                    index += 1
                    while index < end and lines[index][:1].isspace():
                        index += 1
                    continue
                if stripped.startswith("picture:"):
                    index += 1
                    continue
                cleaned.append(lines[index])
                index += 1
            lines = cleaned + lines[end:]

    result = "".join(lines)
    result = MARKDOWN_IMAGE.sub(lambda match: match.group(1).strip(), result)
    return HTML_IMAGE.sub("", result)


def clean_posts() -> int:
    changed = 0
    paths = sorted((ROOT / "_posts").glob("*.md"))
    paths.extend(sorted((ROOT / "sites").glob("*/_posts/*.md")))
    for path in paths:
        before = path.read_text(encoding="utf-8")
        after = image_free_markdown(before)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed += 1
    return changed


def clean_site_configs() -> int:
    changed = 0
    for path in sorted((ROOT / "sites").glob("*/site.json")):
        config = json.loads(path.read_text(encoding="utf-8"))
        before = json.dumps(config, sort_keys=True, ensure_ascii=False)
        config.pop("images", None)
        author = config.get("author")
        if isinstance(author, dict):
            author.pop("picture", None)
        after = json.dumps(config, sort_keys=True, ensure_ascii=False)
        if after == before:
            continue
        temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
        temporary.write_text(
            json.dumps(config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, path)
        changed += 1
    return changed


def main() -> None:
    posts = clean_posts()
    configs = clean_site_configs()
    print(f"Removed image data from {posts} posts and {configs} site configs.")


if __name__ == "__main__":
    main()
