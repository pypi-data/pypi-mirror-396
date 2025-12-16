import subprocess
from pathlib import Path

from jps_release_audit_utils.git_true_changes_report import parse_diff_output


def test_detect_real_changes(temp_git_repo):
    repo = temp_git_repo

    # Create file
    f = repo / "hello.txt"
    f.write_text("hello\n")
    subprocess.run(["git", "add", "hello.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True)

    # Modify file with real content change
    f.write_text("hello world\n")

    # Run diff
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

    assert len(parsed.changes) == 1
    ch = parsed.changes[0]
    assert ch.path == "hello.txt"
    assert ch.added == 1
    assert ch.deleted == 1  # replaced text
