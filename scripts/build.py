"""Fetch public data, validate all cards, and refresh README image versions."""

import json
import os
import re
import sys
from pathlib import Path
from xml.etree import ElementTree

from github_stats import fetch_stats
from svg_cards import THEMES, hero, skills, stats


ROOT = Path(__file__).resolve().parent.parent


def main():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise RuntimeError("Set GITHUB_TOKEN or GH_TOKEN; no credentials are stored in the repository")
    data = fetch_stats(token)
    rendered = {}
    for theme in THEMES:
        for card, content in (("hero", hero(theme)), ("skills", skills(theme)), ("stats", stats(theme, data))):
            ElementTree.fromstring(content)
            rendered[f"{card}-{theme}.svg"] = content
    version = re.sub(r"\D", "", data["updated_at"])
    readme_path = ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    readme, replacements = re.subn(
        r'((?:\./assets/(?:hero|skills|stats)-(?:dark|light)|https://raw\.githubusercontent\.com/ylongw/ylongw/output/github-contribution-grid-snake(?:-dark)?)\.svg)(?:\?v=[\w-]+)?',
        lambda match: f"{match[1]}?v={version}", readme,
    )
    if replacements != 8:
        raise RuntimeError(f"Expected eight themed image references in README; found {replacements}")
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    for name, content in rendered.items():
        (assets / name).write_text(content, encoding="utf-8")
    (assets / "stats.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    readme_path.write_text(readme, encoding="utf-8")
    print(f"Generated six SVG cards: {data['public_repositories']} public repos, {data['total_contributions']} public contributions")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError) as error:
        print(f"Profile refresh failed: {error}", file=sys.stderr)
        sys.exit(1)
