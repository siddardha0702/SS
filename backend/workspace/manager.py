import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from backend.config import settings

def get_git_command() -> str:
    git_bin = shutil.which("git")
    if git_bin:
        return git_bin
    for fallback in [
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe"
    ]:
        if os.path.exists(fallback):
            return fallback
    return "git"

class WorkspaceManager:
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or settings.WORKSPACE_BASE_DIR).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_task_dir(self, task_id: str) -> Path:
        return self.base_dir / f"task_{task_id}"

    def create_workspace(self, task_id: str, repo_source: Optional[str] = None) -> Dict[str, str]:
        """
        Creates an isolated workspace directory structure for the task:
        task_<id>/
          ├── repository/
          ├── logs/
          ├── screenshots/
          ├── test-results/
          └── artifacts/
        """
        task_dir = self.get_task_dir(task_id)
        repo_dir = task_dir / "repository"
        logs_dir = task_dir / "logs"
        screenshots_dir = task_dir / "screenshots"
        test_results_dir = task_dir / "test-results"
        artifacts_dir = task_dir / "artifacts"

        for directory in [repo_dir, logs_dir, screenshots_dir, test_results_dir, artifacts_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        git_cmd = get_git_command()

        # An explicit empty string means "start a new project".
        # None is reserved for the legacy demo default.
        if repo_source is not None:
            source = repo_source.strip()
            if not source:
                # Keep the repository directory empty for a fresh application.
                pass
            elif source.startswith(("http://", "https://", "git@")):
                try:
                    subprocess.run(
                        [git_cmd, "clone", source, str(repo_dir)],
                        check=True,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                except Exception as e:
                    raise RuntimeError(f"Failed to clone repository {source}: {str(e)}")
            elif os.path.exists(source):
                shutil.copytree(source, repo_dir, dirs_exist_ok=True)
            else:
                raise FileNotFoundError(f"Repository source does not exist: {source}")
        else:
            # Preserve the explicit legacy demo behavior only when no source was supplied.
            sample_repo_path = Path("sample_repo").resolve()
            if sample_repo_path.is_dir() and any(sample_repo_path.iterdir()):
                shutil.copytree(sample_repo_path, repo_dir, dirs_exist_ok=True)

        # Enforce that repo_dir is strictly its own initialized Git repository
        git_dir = repo_dir / ".git"
        if not git_dir.is_dir():
            subprocess.run([git_cmd, "init"], cwd=str(repo_dir), check=False, capture_output=True)
            subprocess.run([git_cmd, "config", "user.name", "Nexus Agent"], cwd=str(repo_dir), check=False, capture_output=True)
            subprocess.run([git_cmd, "config", "user.email", "agent@nexus.ai"], cwd=str(repo_dir), check=False, capture_output=True)
            subprocess.run([git_cmd, "add", "."], cwd=str(repo_dir), check=False, capture_output=True)
            subprocess.run([git_cmd, "commit", "-m", "Initial baseline commit"], cwd=str(repo_dir), check=False, capture_output=True)

        return {
            "task_dir": str(task_dir),
            "repository": str(repo_dir),
            "logs": str(logs_dir),
            "screenshots": str(screenshots_dir),
            "test_results": str(test_results_dir),
            "artifacts": str(artifacts_dir),
        }

    def resolve_safe_path(self, task_id: str, relative_path: str) -> Path:
        """
        Ensures target path is strictly within the repository sandbox.
        Prevents directory traversal attacks.
        """
        repo_dir = (self.get_task_dir(task_id) / "repository").resolve()
        target = (repo_dir / relative_path).resolve()
        try:
            target.relative_to(repo_dir)
        except ValueError:
            raise ValueError(f"Access denied: Path '{relative_path}' escapes workspace repository sandbox.")
        return target

    def cleanup_workspace(self, task_id: str):
        task_dir = self.get_task_dir(task_id)
        if task_dir.exists():
            shutil.rmtree(task_dir, ignore_errors=True)

workspace_manager = WorkspaceManager()
