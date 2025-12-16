from __future__ import annotations

"""
git_true_changes_report.py

Implements the `audit-changes` command for jps-release-audit-utils.

Features:
- Detects *true* content changes in the working tree
- Ignores mode-only / permission-only changes
- Ignores rename-only changes (no content change)
- Optional whitespace-insensitive diff
- Optional ignore-dirs and ignore-globs filtering
- Multiple output formats: text, json, markdown
- Configurable via:
    1) ~/.config/jps-release-audit-utils/config.yaml
    2) package-local conf/config.yaml
- Typer-based CLI entrypoint: `audit-changes`
"""

import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import fnmatch
import typer
import yaml

# --------------------------------------------------------------------------- #
# Data models
# --------------------------------------------------------------------------- #


@dataclass
class FileChange:
    """Represents a true content change for a single file."""

    path: str
    added: int  # -1 == binary change
    deleted: int  # -1 == binary change


@dataclass
class AuditChangesConfig:
    """Configurable behavior for `audit-changes`."""

    ignore_whitespace: bool = False
    ignore_dirs: List[str] = field(default_factory=list)
    ignore_globs: List[str] = field(default_factory=list)
    default_format: str = "text"  # text|json|markdown
    verbose_default: bool = False
    fail_if_changed_default: bool = False


# --------------------------------------------------------------------------- #
# Config loading (Option C: global + repo-local)
# --------------------------------------------------------------------------- #


def _load_yaml_file(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            return {}
        return data
    except Exception:
        # For robustness, ignore broken config files and fall back to defaults.
        return {}


def _apply_mapping_to_config(cfg: AuditChangesConfig, mapping: Dict[str, Any]) -> AuditChangesConfig:
    """
    Apply config values from mapping to cfg.

    Expected shape:

    audit_changes:
      ignore_whitespace: true
      ignore_dirs:
        - .venv
        - dist
      ignore_globs:
        - "*.md"
      default_format: "markdown"
      verbose_default: true
      fail_if_changed_default: false
    """
    section = mapping.get("audit_changes") or {}
    if not isinstance(section, dict):
        return cfg

    if "ignore_whitespace" in section:
        cfg.ignore_whitespace = bool(section["ignore_whitespace"])

    if "ignore_dirs" in section and isinstance(section["ignore_dirs"], list):
        cfg.ignore_dirs = [str(x) for x in section["ignore_dirs"]]

    if "ignore_globs" in section and isinstance(section["ignore_globs"], list):
        cfg.ignore_globs = [str(x) for x in section["ignore_globs"]]

    if "default_format" in section:
        cfg.default_format = str(section["default_format"])

    if "verbose_default" in section:
        cfg.verbose_default = bool(section["verbose_default"])

    if "fail_if_changed_default" in section:
        cfg.fail_if_changed_default = bool(section["fail_if_changed_default"])

    return cfg


def load_effective_config() -> AuditChangesConfig:
    """
    Load configuration with Option C precedence:

    1. Global config: ~/.config/jps-release-audit-utils/config.yaml
    2. Repo-local config: <package>/conf/config.yaml

    CLI options will later override/extend this base config.
    """
    cfg = AuditChangesConfig()

    # 1. Global config (~/.config/jps-release-audit-utils/config.yaml)
    global_conf = Path.home() / ".config" / "jps-release-audit-utils" / "config.yaml"
    cfg = _apply_mapping_to_config(cfg, _load_yaml_file(global_conf))

    # 2. Repo-local config (<this_package>/conf/config.yaml)
    package_root = Path(__file__).resolve().parent
    local_conf = package_root / "conf" / "config.yaml"
    cfg = _apply_mapping_to_config(cfg, _load_yaml_file(local_conf))

    return cfg


# --------------------------------------------------------------------------- #
# Git diff helpers
# --------------------------------------------------------------------------- #


def _run_git_diff_numstat(ignore_whitespace: bool) -> Tuple[str, str, int]:
    """
    Run git diff to get numstat + summary output.

    Return: (stdout, stderr, returncode)
    """
    cmd = ["git", "diff", "--numstat", "--summary"]
    if ignore_whitespace:
        cmd.append("-w")

    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        check=False,
    )

    return result.stdout, result.stderr, result.returncode


def _should_ignore_path(path: str, ignore_dirs: Iterable[str], ignore_globs: Iterable[str]) -> bool:
    """
    Decide whether to ignore a path based on directory prefixes and glob patterns.
    """
    norm_path = path.strip()
    # Directory-based ignores
    for d in ignore_dirs:
        d = d.strip().rstrip("/")
        if not d:
            continue
        # Simple prefix check: "dir" or "dir/..."
        if norm_path == d or norm_path.startswith(d + "/"):
            return True

    # Glob-based ignores
    for pattern in ignore_globs:
        if fnmatch.fnmatch(norm_path, pattern):
            return True

    return False


@dataclass
class ParsedDiff:
    changes: List[FileChange]
    metadata_only_paths: List[str]
    ignored_paths: List[str]
    raw_output: str


def parse_diff_output(
    diff_output: str,
    ignore_dirs: Iterable[str],
    ignore_globs: Iterable[str],
) -> ParsedDiff:
    """
    Parse `git diff --numstat --summary` output to determine true content changes.

    Rules:
    - A numstat line has the form: "<added>\t<deleted>\t<path>"
    - added/deleted == "-" => binary change => treated as true content change
    - added == 0 and deleted == 0 => metadata-only (rename-only, mode-only, etc.)
    - Paths matching ignore_dirs / ignore_globs are skipped entirely
    """
    changes: List[FileChange] = []
    metadata_only_paths: List[str] = []
    ignored_paths: List[str] = []

    for line in diff_output.splitlines():
        if "\t" not in line:
            # Not a numstat line (likely a summary line)
            continue

        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue

        added_str, deleted_str, path = parts
        path = path.strip()

        if _should_ignore_path(path, ignore_dirs, ignore_globs):
            if path not in ignored_paths:
                ignored_paths.append(path)
            continue

        # Binary change
        if added_str == "-" or deleted_str == "-":
            changes.append(FileChange(path=path, added=-1, deleted=-1))
            continue

        try:
            added = int(added_str)
            deleted = int(deleted_str)
        except ValueError:
            # Unexpected content; treat conservatively and skip
            if path not in metadata_only_paths:
                metadata_only_paths.append(path)
            continue

        if added == 0 and deleted == 0:
            # No text diff => metadata-only change (rename-only, mode-only, etc.)
            if path not in metadata_only_paths:
                metadata_only_paths.append(path)
            continue

        # True content change
        changes.append(FileChange(path=path, added=added, deleted=deleted))

    return ParsedDiff(
        changes=changes,
        metadata_only_paths=metadata_only_paths,
        ignored_paths=ignored_paths,
        raw_output=diff_output,
    )


# --------------------------------------------------------------------------- #
# Formatting helpers
# --------------------------------------------------------------------------- #


def format_changes_text(parsed: ParsedDiff, verbose: bool) -> str:
    lines: List[str] = []

    if not parsed.changes:
        lines.append("No true content modifications detected.")
    else:
        lines.append("True content modifications:")
        lines.append("---------------------------")
        for ch in parsed.changes:
            if ch.added == -1 and ch.deleted == -1:
                lines.append(f"Binary change: {ch.path}")
            else:
                lines.append(f"{ch.path} (+{ch.added}, -{ch.deleted})")

    if verbose:
        lines.append("")
        if parsed.metadata_only_paths:
            lines.append("Metadata-only changes (mode/rename/etc.):")
            for p in sorted(parsed.metadata_only_paths):
                lines.append(f"  {p}")
        if parsed.ignored_paths:
            lines.append("")
            lines.append("Ignored paths (ignore-dirs/ignore-globs):")
            for p in sorted(parsed.ignored_paths):
                lines.append(f"  {p}")

    return "\n".join(lines)


def format_changes_json(parsed: ParsedDiff, verbose: bool) -> str:
    payload: Dict[str, Any] = {
        "changes": [
            {
                "path": ch.path,
                "added": ch.added,
                "deleted": ch.deleted,
                "binary": (ch.added == -1 and ch.deleted == -1),
            }
            for ch in parsed.changes
        ]
    }

    if verbose:
        payload["metadata_only_paths"] = sorted(parsed.metadata_only_paths)
        payload["ignored_paths"] = sorted(parsed.ignored_paths)

    return json.dumps(payload, indent=2)


def format_changes_markdown(parsed: ParsedDiff, verbose: bool) -> str:
    lines: List[str] = []

    lines.append("# Audit: True Content Changes")
    lines.append("")

    if not parsed.changes:
        lines.append("_No true content modifications detected._")
    else:
        lines.append("| Path | Added | Deleted | Binary |")
        lines.append("|------|-------|---------|--------|")
        for ch in parsed.changes:
            is_binary = ch.added == -1 and ch.deleted == -1
            added = "-" if is_binary else str(ch.added)
            deleted = "-" if is_binary else str(ch.deleted)
            lines.append(f"| `{ch.path}` | {added} | {deleted} | {str(is_binary).lower()} |")

    if verbose:
        if parsed.metadata_only_paths:
            lines.append("")
            lines.append("## Metadata-only changes")
            for p in sorted(parsed.metadata_only_paths):
                lines.append(f"- `{p}`")

        if parsed.ignored_paths:
            lines.append("")
            lines.append("## Ignored paths")
            for p in sorted(parsed.ignored_paths):
                lines.append(f"- `{p}`")

    return "\n".join(lines)


def render_output(parsed: ParsedDiff, fmt: str, verbose: bool) -> str:
    fmt = fmt.lower()
    if fmt == "json":
        return format_changes_json(parsed, verbose)
    if fmt == "markdown":
        return format_changes_markdown(parsed, verbose)
    # default / fallback
    return format_changes_text(parsed, verbose)


# --------------------------------------------------------------------------- #
# Typer CLI
# --------------------------------------------------------------------------- #

app = typer.Typer(help="Utilities for auditing working tree changes.")


@app.command("audit-changes")
def audit_changes(
    ignore_whitespace: Optional[bool] = typer.Option(
        None,
        "--ignore-whitespace/--no-ignore-whitespace",
        help="Ignore whitespace-only changes (similar to `git diff -w`).",
    ),
    ignore_dir: List[str] = typer.Option(
        [],
        "--ignore-dir",
        "-I",
        help="Directory prefix to ignore (can be provided multiple times).",
    ),
    ignore_glob: List[str] = typer.Option(
        [],
        "--ignore-glob",
        help="Glob pattern to ignore (can be provided multiple times).",
    ),
    output_format: Optional[str] = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format: text|json|markdown. Defaults to config.default_format.",
    ),
    verbose: Optional[bool] = typer.Option(
        None,
        "--verbose/--quiet",
        help="Include metadata-only and ignored paths in the report.",
    ),
    fail_if_changed: Optional[bool] = typer.Option(
        None,
        "--fail-if-changed/--no-fail-if-changed",
        help="Exit with non-zero status if any true content changes are detected.",
    ),
) -> None:
    """
    Report files with true content modifications, ignoring metadata-only changes
    such as mode / permission flips and pure renames.
    """
    base_cfg = load_effective_config()

    # Resolve effective settings
    effective_ignore_whitespace = (
        ignore_whitespace if ignore_whitespace is not None else base_cfg.ignore_whitespace
    )
    # Lists: config values + CLI additions
    effective_ignore_dirs = list(base_cfg.ignore_dirs) + list(ignore_dir)
    effective_ignore_globs = list(base_cfg.ignore_globs) + list(ignore_glob)

    effective_format = (output_format or base_cfg.default_format).lower()
    if effective_format not in {"text", "json", "markdown"}:
        raise typer.BadParameter("format must be one of: text, json, markdown")

    effective_verbose = verbose if verbose is not None else base_cfg.verbose_default
    effective_fail_if_changed = (
        fail_if_changed if fail_if_changed is not None else base_cfg.fail_if_changed_default
    )

    stdout, stderr, rc = _run_git_diff_numstat(ignore_whitespace=effective_ignore_whitespace)

    # git diff exits with:
    #   0 => no differences
    #   1 => differences found
    #  >1 => error
    if rc > 1:
        typer.echo("Error: git diff failed.", err=True)
        if stderr:
            typer.echo(stderr, err=True)
        raise typer.Exit(code=rc)

    if not stdout.strip():
        # No differences at all
        parsed = ParsedDiff(changes=[], metadata_only_paths=[], ignored_paths=[], raw_output=stdout)
    else:
        parsed = parse_diff_output(
            stdout,
            ignore_dirs=effective_ignore_dirs,
            ignore_globs=effective_ignore_globs,
        )

    output = render_output(parsed, fmt=effective_format, verbose=effective_verbose)
    typer.echo(output)

    if effective_fail_if_changed and parsed.changes:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
