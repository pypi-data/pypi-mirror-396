#!/usr/bin/env python3
"""
commit_report.py

Generate an Excel report comparing commits across multiple Git branches.

Features:
- Reads branch commit history using GitPython.
- Produces an .xlsx file with four worksheets:
    1. timeline_by_date      (chronological commit timeline)
    2. timeline_by_topology  (Git DAG / topo-order timeline)
    3. timeline_hybrid       (both date + topo indices, out-of-order flags)
    4. analytics_summary     (counts, unique/missing commits per branch, etc.)

- Branches are provided via:
    --branches       (comma-separated)
    --branches-file  (newline-separated list)

- Sheet names and colors are configurable via YAML:
    src/jps_release_audit_utils/conf/config.yaml

Default sheet names (overridable by YAML):
    timeline_by_date
    timeline_by_topology
    timeline_hybrid
    analytics_summary

Default colors (overridable by YAML):
    missing:      FFC7CE  (light red)
    all_present:  C6EFCE  (light green)
    out_of_order: FFEB9C  (light yellow)

Color semantics:
- Branch cells with "MISSING" => missing color.
- Branch cells when commit is in *all* branches => all_present color.
- Out-of-order commits (date earlier than previous topo commit's date):
    - timeline_by_topology: Date cell highlighted with out_of_order color.
    - timeline_hybrid: OutOfOrder cell highlighted with out_of_order color.

All sheets:
- Header row frozen (A2)
- Auto-filter enabled on header row
- Columns auto-sized

Usage (example):

    python -m jps_release_audit_utils.commit_report \
        --repo-path /path/to/repo \
        --branches develop,main,release/v5.8.0-rc \
        --output commit_report.xlsx

Or:

    python -m jps_release_audit_utils.commit_report \
        --repo-path /path/to/repo \
        --branches-file branches.txt \
        --output commit_report.xlsx

"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Optional

from datetime import datetime

import typer
from git import Repo
from openpyxl import Workbook

from .constants import DEFAULT_CONFIG_PATH
from .config_loader import load_config
from .repo_helper import load_branches
from .excel_writer import (
    write_sheet_analytics,
    write_sheet_by_date,
    write_sheet_by_topology,
    write_sheet_hybrid,
)
from .git_ops import get_branch_commits, get_topo_sorted_commits

logger = logging.getLogger("commit-report")


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logger.debug("Verbose logging enabled.")


app = typer.Typer(add_completion=False)


@app.command()
def generate(
    repo_path: str = typer.Option(
        ".",
        help="Path to a local git repository (default: current working directory).",
    ),
    output: str = typer.Option(
        "commit_report.xlsx",
        help="Output Excel file path (default: commit_report.xlsx in CWD).",
    ),
    branches: Optional[str] = typer.Option(
        None,
        help="Comma-separated list of branches to inspect.",
    ),
    branches_file: Optional[str] = typer.Option(
        None,
        help="Path to file with newline-separated branches to inspect.",
    ),
    config: Optional[str] = typer.Option(
        None,
        help=(
            "Path to YAML configuration file. "
            "If not provided, defaults to conf/config.yaml within the package "
            "(if present), otherwise built-in defaults are used."
        ),
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose (DEBUG) logging.",
    ),
) -> None:
    """
    Generate an Excel report comparing commits across branches.
    """
    setup_logging(verbose)

    # Resolve config path
    if config is not None:
        config_path = Path(config).resolve()
        sheet_names, colors = load_config(config_path, required=True)
    else:
        sheet_names, colors = load_config(DEFAULT_CONFIG_PATH, required=False)

    branch_list = load_branches(branches, branches_file)
    logger.info("Using branches: %s", branch_list)

    repo = Repo(repo_path)
    if repo.bare:
        raise typer.Exit("ERROR: Provided path is not a valid git repository.")

    # Step 1: Collect commits per branch
    per_branch: Dict[str, Dict[str, dict]] = {}
    for branch in branch_list:
        per_branch[branch] = get_branch_commits(repo, branch)

    # Step 2: Merge into a unified all_commits map
    # all_commits[hash] = {
    #   "hash": ...,
    #   "datetime": ...,
    #   "date": ...,
    #   "message": ...,
    #   "author": ...,
    #   "pr": ...,
    #   "branches": set([...]),
    #   "topo_index": int,
    #   "date_index": int,
    #   "out_of_order": bool,
    # }
    all_commits: Dict[str, dict] = {}

    for branch, commit_map in per_branch.items():
        for commit_hash, meta in commit_map.items():
            if commit_hash not in all_commits:
                all_commits[commit_hash] = {
                    "hash": commit_hash,
                    "datetime": meta["datetime"],
                    "date": meta["date"],
                    "message": meta["message"],
                    "author": meta["author"],
                    "pr": meta["pr"],
                    "branches": set([branch]),
                }
            else:
                all_commits[commit_hash]["branches"].add(branch)

    logger.info("Total unique commits across all branches: %d", len(all_commits))

    # Step 3: Assign topo_index
    topo_commits = get_topo_sorted_commits(repo, branch_list)
    topo_idx = 1
    for commit_hash in topo_commits:
        if commit_hash in all_commits:
            all_commits[commit_hash]["topo_index"] = topo_idx
            topo_idx += 1

    # Step 4: Assign date_index based on chronological sort
    chronological = sorted(
        all_commits.items(),
        key=lambda kv: (kv[1]["datetime"], kv[0]),
    )
    for idx, (commit_hash, _) in enumerate(chronological, start=1):
        all_commits[commit_hash]["date_index"] = idx

    # Step 5: Determine out_of_order based on topo sequence
    prev_dt: Optional[datetime] = None
    for commit_hash in topo_commits:
        if commit_hash not in all_commits:
            continue
        meta = all_commits[commit_hash]
        dt = meta["datetime"]
        if prev_dt is None:
            meta["out_of_order"] = False
        else:
            meta["out_of_order"] = dt < prev_dt
        prev_dt = dt

    # Step 6: Write Excel workbook
    wb = Workbook()
    # Remove default empty sheet
    wb.remove(wb.active)

    # Sheet 1: timeline_by_date
    write_sheet_by_date(
        wb=wb,
        all_commits=all_commits,
        branches=branch_list,
        sheet_name=sheet_names["timeline_by_date"],
        colors=colors,
    )

    # Sheet 2: timeline_by_topology
    write_sheet_by_topology(
        wb=wb,
        topo_commits=topo_commits,
        all_commits=all_commits,
        branches=branch_list,
        sheet_name=sheet_names["timeline_by_topology"],
        colors=colors,
    )

    # Sheet 3: timeline_hybrid
    write_sheet_hybrid(
        wb=wb,
        topo_commits=topo_commits,
        all_commits=all_commits,
        branches=branch_list,
        sheet_name=sheet_names["timeline_hybrid"],
        colors=colors,
    )

    # Sheet 4: analytics_summary
    write_sheet_analytics(
        wb=wb,
        all_commits=all_commits,
        branches=branch_list,
        sheet_name=sheet_names["analytics_summary"],
    )

    outpath = Path(output).resolve()
    wb.save(outpath)
    logger.info("Excel report written to: %s", outpath)


# ============================================================
if __name__ == "__main__":
    app()
