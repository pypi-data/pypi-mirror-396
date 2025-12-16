#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
help.py

Lists all available CLI tools in the jps-release-audit-utils package
along with their purpose and usage examples.

This script provides a unified help command for developers and QA/release
engineers to understand the purpose of each entrypoint utility included
in this package.

Usage:
    jps-release-audit-utils-help
"""

import textwrap


def main() -> None:
    """Display help for all entrypoint scripts in this package."""
    help_text = textwrap.dedent(
        """
    🧾 jps-release-audit-utils — Available Commands
    ==============================================

    jps-release-audit-utils-commit-report
        Generate an Excel report comparing commits across multiple Git branches.

        Key features:
        - Reads branch commit history (GitPython)
        - Multi-branch comparison
        - Produces a multi-sheet .xlsx report (timelines + analytics)

        Example:
            jps-release-audit-utils-commit-report \\
                --repo-path /path/to/repo \\
                --branches main develop release/v2.3.0-rc

    audit-changes
        Report *true content* modifications in the working tree, ignoring
        metadata-only changes (mode/permission flips, rename-only changes).

        Key features:
        - Uses: `git diff --numstat --summary` (optionally `-w`)
        - Ignores:
            * mode-only / permission-only changes
            * rename-only changes with no content change
        - Optional whitespace-insensitive diff
        - Optional filtering via --ignore-dir and --ignore-glob
        - Output formats: text, json, markdown
        - Configurable via:
            1) ~/.config/jps-release-audit-utils/config.yaml
            2) package-local conf/config.yaml

        Examples:
            audit-changes
            audit-changes --ignore-whitespace
            audit-changes --format json --verbose
            audit-changes -I .venv -I dist --ignore-glob "*.md"
            audit-changes --fail-if-changed

    jps-release-audit-utils-help
        Displays this overview of all available commands.

    ----------------------------------------------------
    Tip: Run each command with '--help' to see detailed options.
    """
    )

    print(help_text)


if __name__ == "__main__":
    main()
