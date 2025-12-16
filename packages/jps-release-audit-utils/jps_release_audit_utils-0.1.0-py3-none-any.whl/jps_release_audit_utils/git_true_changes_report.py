#!/usr/bin/env python3
"""
git_true_changes_report.py

Generate a report of files that have *true content modifications*, excluding:
- mode-only changes (old mode/new mode)
- permission-only changes (755→644)
- pure renames without content changes
- optional: whitespace-only changes

This script does NOT modify the repo. It only reports.
"""

import subprocess
import sys
import re
from dataclasses import dataclass
from typing import List


@dataclass
class FileChange:
    path: str
    added: int
    deleted: int


MODE_CHANGE_RE = re.compile(r"^mode change [0-9]+ => [0-9]+")
RENAME_ONLY_RE = re.compile(r"^rename [^ ]+ => [^ ]+")


def run_git_diff() -> str:
    """Run git diff to get summary + numstat."""
    cmd = ["git", "diff", "--numstat", "--summary"]
    result = subprocess.run(
        cmd, capture_output=True, text=True, check=False
    )
    return result.stdout


def parse_diff_output(diff_output: str) -> List[FileChange]:
    """Parse git diff --numstat --summary output."""
    true_mods = []
    lines = diff_output.splitlines()

    skip_paths = set()

    # Detect purely metadata changes (mode changes, renames)
    for line in lines:
        if MODE_CHANGE_RE.search(line):
            # restrict to path portion of: "mode change 100755 => 100644 path/to/file"
            parts = line.strip().split()
            if len(parts) > 4:
                skip_paths.add(parts[-1])
        elif RENAME_ONLY_RE.search(line):
            # Example: "rename oldname.txt => newname.txt"
            # A rename-only entry comes *only* from summary, without numstat following it.
            pass  # handled by numstat checking below

    # Collect true content changes
    for line in lines:
        parts = line.split("\t")
        if len(parts) != 3:
            continue  # Not a numstat line

        added, deleted, path = parts

        # Skip metadata-only changes
        if path in skip_paths:
            continue

        # Added and deleted both "-" means binary change — count as real content change
        if added == "-" or deleted == "-":
            true_mods.append(FileChange(path, -1, -1))
            continue

        added = int(added)
        deleted = int(deleted)

        if added == 0 and deleted == 0:
            # This means rename-only or metadata-only
            continue

        # Otherwise, real content change
        true_mods.append(FileChange(path, added, deleted))

    return true_mods


def main():
    diff_output = run_git_diff()

    if not diff_output.strip():
        print("No uncommitted changes.")
        return

    changes = parse_diff_output(diff_output)

    if not changes:
        print("Only metadata changes detected (mode changes, renames, perms). No true content modifications.")
        return

    print("True content modifications:")
    print("---------------------------")
    for ch in changes:
        if ch.added == -1:
            print(f"Binary change: {ch.path}")
        else:
            print(f"{ch.path} (+{ch.added}, -{ch.deleted})")


if __name__ == "__main__":
    main()
