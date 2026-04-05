"""
Version bump helper script for tornadoapi-guard.

Updates the version string across all files that reference it:
- pyproject.toml
- CHANGELOG.md
- docs/release-notes.md

Usage:
    python .github/scripts/bump_version.py <version>
    make bump-version VERSION=x.y.z

No external dependencies required — stdlib only.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

# Resolve project root relative to this script's location
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def parse_semver(version: str) -> tuple[int, ...]:
    """Parse a semver string into a comparable tuple."""
    return tuple(int(part) for part in version.split("."))


def update_pyproject_toml(version: str) -> bool:
    """Update version in pyproject.toml."""
    path = PROJECT_ROOT / "pyproject.toml"
    content = path.read_text()
    pattern = re.compile(r'^(version\s*=\s*)"[^"]*"', re.MULTILINE)
    match = pattern.search(content)
    if not match:
        print("  ERROR: Could not find version field in pyproject.toml")
        return False
    current = re.search(r'"([^"]*)"', match.group(0))
    if current and current.group(1) == version:
        print(f"  pyproject.toml: already set to {version}")
        return True
    new_content = pattern.sub(f'{match.group(1)}"{version}"', content)
    path.write_text(new_content)
    print(f"  pyproject.toml: updated to {version}")
    return True


def _insert_changelog_scaffold(path: Path, version: str, label: str) -> bool:
    """Insert a version scaffold block into a changelog file."""
    content = path.read_text()
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    header = f"v{version} ({today})"

    # Check if this version already has an entry
    if f"v{version} (" in content:
        print(f"  {label}: v{version} entry already exists")
        return True

    scaffold = (
        f"{header}\n"
        f"-------------------\n"
        f"\n"
        f"TITLE (v{version})\n"
        f"------------\n"
        f"\n"
        f"CONTENT\n"
        f"\n"
        f"___\n"
        f"\n"
    )

    # Find the first existing version entry to insert before it
    version_header_pattern = re.compile(r"^v\d+\.\d+\.\d+ \(", re.MULTILINE)
    match = version_header_pattern.search(content)
    if match:
        insert_pos = match.start()
        new_content = content[:insert_pos] + scaffold + content[insert_pos:]
    else:
        # No existing entries — append at end
        new_content = content.rstrip() + "\n\n" + scaffold

    path.write_text(new_content)
    print(f"  {label}: added v{version} scaffold")
    return True


def update_changelogs(version: str) -> bool:
    """Update CHANGELOG.md and docs/release-notes.md."""
    changelog = PROJECT_ROOT / "CHANGELOG.md"
    release_notes = PROJECT_ROOT / "docs" / "release-notes.md"

    ok = True
    ok = _insert_changelog_scaffold(changelog, version, "CHANGELOG.md") and ok
    if release_notes.exists():
        ok = (
            _insert_changelog_scaffold(release_notes, version, "docs/release-notes.md")
            and ok
        )
    return ok


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: bump_version.py <version>")
        print("  version must be in X.Y.Z format")
        return 1

    version = sys.argv[1]

    if not VERSION_PATTERN.match(version):
        print(f"Error: '{version}' is not a valid version. Expected format: X.Y.Z")
        return 1

    print(f"Bumping version to {version}...\n")

    updaters: list[tuple[str, Callable[[str], bool]]] = [
        ("pyproject.toml", update_pyproject_toml),
        ("changelogs", update_changelogs),
    ]

    all_ok = True
    for name, updater in updaters:
        try:
            if not updater(version):
                print(f"\n  FAILED: {name}")
                all_ok = False
        except Exception as e:
            print(f"\n  ERROR updating {name}: {e}")
            all_ok = False

    print()
    if all_ok:
        print("Version bump complete.")
    else:
        print("Version bump completed with errors.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
