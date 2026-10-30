import subprocess

from backend.workspace.manager import WorkspaceManager


def test_empty_repository_source_creates_blank_project(tmp_path, monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 0, stdout="", stderr="")

    monkeypatch.setattr("backend.workspace.manager.subprocess.run", fake_run)
    manager = WorkspaceManager(base_dir=str(tmp_path))
    paths = manager.create_workspace("new-project-test", repo_source="")

    repo_dir = manager.get_task_dir("new-project-test") / "repository"
    assert paths["repository"] == str(repo_dir)
    assert repo_dir.is_dir()
    assert list(repo_dir.iterdir()) == []


def test_invalid_repository_source_is_not_silently_treated_as_new_project(tmp_path):
    manager = WorkspaceManager(base_dir=str(tmp_path))
    try:
        manager.create_workspace("invalid-source-test", repo_source="missing-repository-path")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Invalid repository source should raise FileNotFoundError")
