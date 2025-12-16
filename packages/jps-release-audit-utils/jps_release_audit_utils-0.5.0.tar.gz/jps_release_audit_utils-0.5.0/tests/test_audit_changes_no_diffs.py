import subprocess
from typer.testing import CliRunner

from jps_release_audit_utils.git_true_changes_report import app

runner = CliRunner()


def test_no_changes_produces_clean_output(temp_git_repo):
    repo = temp_git_repo

    f = repo / "clean.txt"
    f.write_text("hello\n")
    subprocess.run(["git", "add", "clean.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True)

    result = runner.invoke(
        app,
        ["audit-changes", "--fail-if-changed"],
        cwd=str(repo),
    )


    assert result.exit_code == 0
    assert "No true content modifications" in result.stdout
