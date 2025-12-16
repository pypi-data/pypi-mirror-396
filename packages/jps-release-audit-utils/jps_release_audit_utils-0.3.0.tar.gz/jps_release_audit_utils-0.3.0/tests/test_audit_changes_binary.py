import subprocess
from pathlib import Path

from jps_release_audit_utils.git_true_changes_report import parse_diff_output


def test_binary_changes_detected(temp_git_repo):
    repo = temp_git_repo

    f = repo / "image.bin"
    f.write_bytes(b"\x00\x01\x02")
    subprocess.run(["git", "add", "image.bin"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True)

    # Modify binary content
    f.write_bytes(b"\x00\x01\x02\x03")

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
    assert ch.path == "image.bin"
    assert ch.added == -1
    assert ch.deleted == -1  # binary sentinel
