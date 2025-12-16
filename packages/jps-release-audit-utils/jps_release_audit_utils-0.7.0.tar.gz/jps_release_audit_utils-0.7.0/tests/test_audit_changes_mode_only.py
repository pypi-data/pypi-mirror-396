import os
import subprocess

from jps_release_audit_utils.git_true_changes_report import parse_diff_output


def test_ignore_mode_only_changes(temp_git_repo):
    repo = temp_git_repo

    f = repo / "script.sh"
    f.write_text("#!/bin/bash\necho hi\n")
    subprocess.run(["git", "add", "script.sh"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True)

    # Flip executable bit (mode change only)
    os.chmod(f, 0o755)

    result = subprocess.run(
        ["git", "diff", "--numstat", "--summary"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )

    parsed = parse_diff_output(
        result.stdout,
        ignore_dirs=[],
        ignore_globs=[],
    )

    # No true content changes
    assert parsed.changes == []
    # Metadata-only path recognized
    assert "script.sh" in parsed.metadata_only_paths
