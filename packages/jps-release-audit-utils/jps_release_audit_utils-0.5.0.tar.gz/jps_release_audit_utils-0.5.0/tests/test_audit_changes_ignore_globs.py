import subprocess

from jps_release_audit_utils.git_true_changes_report import parse_diff_output


def test_ignore_glob_patterns(temp_git_repo):
    repo = temp_git_repo

    f = repo / "notes.md"
    f.write_text("initial\n")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True)

    # Modify markdown file
    f.write_text("updated\n")

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
        ignore_globs=["*.md"],
    )

    assert parsed.changes == []
    assert "notes.md" in parsed.ignored_paths
