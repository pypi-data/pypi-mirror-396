import subprocess

from jps_release_audit_utils.git_true_changes_report import parse_diff_output


def test_ignore_dir_filtering(temp_git_repo):
    repo = temp_git_repo

    # Create ignored directory
    ignored = repo / "build"
    ignored.mkdir()

    f = ignored / "artifact.txt"
    f.write_text("artifact\n")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True)

    # Modify file inside ignored dir
    f.write_text("artifact modified\n")

    result = subprocess.run(
        ["git", "diff", "--numstat", "--summary"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )

    parsed = parse_diff_output(
        result.stdout,
        ignore_dirs=["build"],
        ignore_globs=[],
    )

    # Should not report true changes
    assert parsed.changes == []
    assert "build/artifact.txt" in parsed.ignored_paths
