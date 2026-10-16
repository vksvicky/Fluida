"""Bump the Fluida application version and format store release notes."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_APPLICATION = re.compile(r'(<iq:application\b[^>]*\bversion=")(\d+\.\d+\.\d+)(")')


def apply_bump(text: str, kind: str, custom: str = "") -> tuple[str, str]:
    """Return the manifest text and the application version after `kind`."""
    found = _APPLICATION.search(text)
    if found is None:
        raise ValueError("manifest has no application version")
    current = found.group(2)
    if kind == "skip":
        return text, current
    updated = _APPLICATION.sub(rf"\g<1>{_next_version(current, kind, custom)}\3", text, count=1)
    version = _APPLICATION.search(updated).group(2)
    return updated, version


def _next_version(current: str, kind: str, custom: str) -> str:
    if kind == "custom":
        if re.fullmatch(r"\d+\.\d+\.\d+", custom) is None:
            raise ValueError(f"version must look like 1.2.3, got {custom!r}")
        return custom
    major, minor, patch = (int(part) for part in current.split("."))
    if kind == "major":
        return f"{major + 1}.0.0"
    if kind == "minor":
        return f"{major}.{minor + 1}.0"
    if kind == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"unknown bump {kind!r}")


def release_notes(version: str) -> str:
    """What's New text for someone installing the face. ASCII only."""
    text = f"""What's New in v{version}:

Fluida is a round watch face with two fluid columns.

* The hour column and the minute column fill as time passes.
* A well above the columns holds the seconds.
* Steps, heart rate, calories, battery, and temperature sit on the dial.
* You can pick a color palette, how much the bubble tilts, and whether the hour change animates.
"""
    return text.encode("ascii", "ignore").decode("ascii")


def main() -> None:
    manifest = Path(sys.argv[1])
    kind = sys.argv[2]
    custom = sys.argv[3] if len(sys.argv) > 3 else ""
    updated, version = apply_bump(manifest.read_text(), kind, custom)
    if kind != "skip":
        manifest.write_text(updated)
    print(version)


if __name__ == "__main__":
    main()
