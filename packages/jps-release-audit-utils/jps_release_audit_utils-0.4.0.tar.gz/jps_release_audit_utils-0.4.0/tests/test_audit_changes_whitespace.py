import subprocess

from jps_release_audit_utils.git_true_changes_report import parse_diff_output


def test_whitespace_only_changes_are_ignored(temp_git_repo):
    repo = temp_git_repo

    f = repo / "code.py"
    f.write_text("x=1\n")
    subprocess.run(["git", "add", "code.py"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True)

    # Whitespace-only change
    f.write_text("x = 1\n")

    # Git diff -w suppresses whitespace-only changes
    result = subprocess.run(
        ["git", "diff", "--numstat", "--summary", "-w"],
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

    # Should detect no true content modifications
    assert parsed.changes == []
