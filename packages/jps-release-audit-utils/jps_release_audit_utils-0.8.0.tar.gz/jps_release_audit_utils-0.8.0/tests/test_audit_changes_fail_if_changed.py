import subprocess
from typer.testing import CliRunner

from jps_release_audit_utils.git_true_changes_report import app


runner = CliRunner()


def test_fail_if_changed_exit_code(temp_git_repo):
    repo = temp_git_repo

    f = repo / "example.txt"
    f.write_text("abc\n")
    subprocess.run(["git", "add", "example.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True)

    # Modify content
    f.write_text("abc def\n")

    # Run command with fail-if-changed
    result = runner.invoke(
        app,
        ["audit-changes", "--fail-if-changed"],
        cwd=str(repo),
)

    # Typer Exit(code=1)
    assert result.exit_code == 1
