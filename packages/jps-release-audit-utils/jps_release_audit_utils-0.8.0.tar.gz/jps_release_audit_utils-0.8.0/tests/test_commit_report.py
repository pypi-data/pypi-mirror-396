import pytest
from typer.testing import CliRunner

from jps_release_audit_utils.config_loader import load_config
from jps_release_audit_utils.constants import DEFAULT_SHEET_NAMES, DEFAULT_COLORS
from jps_release_audit_utils.commit_report import app

runner = CliRunner()


def test_cli_help_runs():
    """Ensure the CLI help command executes successfully."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout or "Usage" in result.stderr


def test_load_config_defaults():
    """Ensure load_config returns default values when config is missing."""
    sheet_names, colors = load_config(config_path=None, required=False)

    assert isinstance(sheet_names, dict)
    assert isinstance(colors, dict)

    assert sheet_names["timeline_by_date"] == DEFAULT_SHEET_NAMES["timeline_by_date"]
    assert colors["missing"] == DEFAULT_COLORS["missing"]


def test_load_config_with_custom_file(tmp_path):
    """Ensure YAML config overrides defaults correctly."""

    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        """
        sheets:
          timeline_by_date: "CustomDateSheet"
        colors:
          missing: "FF0000"
        """,
        encoding="utf-8",
    )

    sheet_names, colors = load_config(cfg, required=True)

    assert sheet_names["timeline_by_date"] == "CustomDateSheet"
    assert colors["missing"] == "FF0000"

    # Non-overridden values remain defaults
    assert sheet_names["timeline_by_topology"] == DEFAULT_SHEET_NAMES["timeline_by_topology"]
    assert colors["all_present"] == DEFAULT_COLORS["all_present"]


def test_cli_runs_with_minimal_args(tmp_path, monkeypatch):
    """
    Sanity check: Patch Repo() so no real git repo is required.
    Validate that CLI executes and fails cleanly with missing branches.
    """

    class DummyRepo:
        bare = False
        branches = {}
        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr("jps_release_audit_utils.commit_report.Repo", DummyRepo)

    output_file = tmp_path / "report.xlsx"

    result = runner.invoke(
        app,
        [
            "--repo-path",
            str(tmp_path),
            "--branches",
            "main",
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code != 0
    assert "does not exist locally" in result.stdout or "does not exist locally" in result.stderr
