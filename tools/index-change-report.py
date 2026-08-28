#!/usr/bin/env python3
"""Decide whether a regenerated archetype index is worth committing.

build-archetype-index.py stamps the day it ran onto every rebuild, so the file
differs even when nothing about the cards has. This compares the archetype data
itself against the committed copy and writes a short Markdown summary.

Prints `changed=true` or `changed=false`, and appends the same to $GITHUB_OUTPUT
and a summary to $GITHUB_STEP_SUMMARY when those are set. Used by
.github/workflows/refresh-archetype-index.yml; run it by hand to preview.
"""

import json
import os
import pathlib
import re
import subprocess
import sys

INDEX = "data/archetype-art.js"
PATTERN = re.compile(r"window\.ARCHETYPE_ART = (\{.*?\});", re.S)


def archetypes(source):
    m = PATTERN.search(source or "")
    return set(json.loads(m.group(1))) if m else set()


def committed():
    r = subprocess.run(["git", "show", f"HEAD:{INDEX}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def emit(changed, summary):
    print(f"changed={'true' if changed else 'false'}")
    print(summary)
    for var, text in (("GITHUB_OUTPUT", f"changed={'true' if changed else 'false'}\n"),
                      ("GITHUB_STEP_SUMMARY", summary + "\n")):
        path = os.environ.get(var)
        if path:
            with open(path, "a", encoding="utf-8") as fh:
                fh.write(text)


def main():
    current = pathlib.Path(INDEX)
    if not current.exists():
        sys.exit(f"{INDEX} is missing — run tools/build-archetype-index.py first.")

    before, after = archetypes(committed()), archetypes(current.read_text(encoding="utf-8"))
    if not after:
        sys.exit(f"Could not read any archetypes out of {INDEX}.")

    added, gone = sorted(after - before), sorted(before - after)
    if not added and not gone:
        emit(False, "Index is unchanged — no archetypes added or removed.")
        return

    lines = [f"### Archetype index updated", "", f"{len(before)} → {len(after)} archetypes", ""]
    if added:
        lines.append(f"**Added ({len(added)}):** " + ", ".join(added))
    if gone:
        lines.append(f"**Removed ({len(gone)}):** " + ", ".join(gone))
    emit(True, "\n".join(lines))


if __name__ == "__main__":
    main()
