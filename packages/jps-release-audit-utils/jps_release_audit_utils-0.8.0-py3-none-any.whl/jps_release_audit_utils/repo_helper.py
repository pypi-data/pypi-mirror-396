import logging
from typing import List, Optional
from pathlib import Path

import typer

from .constants import PR_REGEX



logger = logging.getLogger(__name__)

def extract_pr_number(message: str) -> str:
    """Extract a PR number (#1234) from the commit message, if present."""
    match = PR_REGEX.search(message)
    return match.group(1) if match else ""


def load_branches(branches: Optional[str], branches_file: Optional[str]) -> List[str]:
    """
    Load branch list from:
        - --branches (comma-separated), or
        - --branches-file (newline-separated)

    Priority:
        1. branches_file
        2. branches
    """
    if branches_file:
        fp = Path(branches_file)
        if not fp.is_file():
            raise typer.Exit(f"ERROR: Branches file not found: {branches_file}")
        branch_list = [line.strip() for line in fp.read_text().splitlines() if line.strip()]
        logger.info("Loaded %d branches from file.", len(branch_list))
        return branch_list

    if branches:
        branch_list = [b.strip() for b in branches.split(",") if b.strip()]
        logger.info("Loaded branches from CLI: %s", branch_list)
        return branch_list

    raise typer.Exit("ERROR: Either --branches or --branches-file must be provided.")

