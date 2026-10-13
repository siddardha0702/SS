import os
import shutil
import subprocess
import re
from typing import Dict, Any, Optional
from backend.workspace.manager import workspace_manager

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

def _sanitize_git_output(text: str) -> str:
    if not text:
        return ""
    return re.sub(r'https://[^@\s]+@github\.com', 'https://***@github.com', text)

def _run_git(task_id: str, args: list) -> subprocess.CompletedProcess:
    repo_dir = (workspace_manager.get_task_dir(task_id) / "repository").resolve()
    task_dir = workspace_manager.get_task_dir(task_id).resolve()

    # Safety check: ensure repo_dir is strictly inside the task workspace directory
    try:
        repo_dir.relative_to(task_dir)
    except ValueError:
        raise ValueError(f"Security violation: Git repository path '{repo_dir}' escapes task sandbox '{task_dir}'.")

    # Safety check: ensure repository has its own .git and does not escape to parent/root git repo
    git_dir = repo_dir / ".git"
    if not git_dir.exists() and args and args[0] != "init":
        raise RuntimeError(f"Sandbox isolation error: '{repo_dir}' is not an initialized Git repository.")

    git_cmd = get_git_command()
    return subprocess.run(
        [git_cmd] + args,
        cwd=str(repo_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

def init_or_branch(task_id: str, branch_name: str) -> Dict[str, Any]:
    repo_dir = (workspace_manager.get_task_dir(task_id) / "repository").resolve()
    git_dir = repo_dir / ".git"

    # Check whether the task workspace itself has its own .git directory
    if not git_dir.is_dir():
        _run_git(task_id, ["init"])
        _run_git(task_id, ["config", "user.name", "Nexus Agent"])
        _run_git(task_id, ["config", "user.email", "agent@nexus.ai"])
        _run_git(task_id, ["add", "."])
        _run_git(task_id, ["commit", "-m", "Initial baseline commit"])

    _run_git(task_id, ["checkout", "-B", branch_name])
    return {"branch": branch_name, "status": "checked_out"}

def git_diff(task_id: str) -> str:
    """Returns the git diff of uncommitted or committed changes."""
    res = _run_git(task_id, ["diff", "HEAD~1"])
    if res.returncode == 0 and res.stdout and res.stdout.strip():
        return res.stdout
    # Try diff of working tree against HEAD
    res2 = _run_git(task_id, ["diff", "HEAD"])
    if res2.returncode == 0 and res2.stdout and res2.stdout.strip():
        return res2.stdout
    # Fallback to unstaged diff
    res3 = _run_git(task_id, ["diff"])
    return res3.stdout or ""

def git_commit(task_id: str, message: str) -> Dict[str, Any]:
    _run_git(task_id, ["config", "user.name", "Nexus Autonomous Agent"])
    _run_git(task_id, ["config", "user.email", "nexus@ai.dev"])
    _run_git(task_id, ["add", "."])
    res = _run_git(task_id, ["commit", "-m", message])
    return {
        "success": res.returncode == 0,
        "stdout": _sanitize_git_output(res.stdout),
        "stderr": _sanitize_git_output(res.stderr)
    }

def setup_remote(task_id: str, remote_url: str, remote_name: str = "origin") -> bool:
    """Configures or updates remote URL strictly inside the isolated task workspace repository."""
    res = _run_git(task_id, ["remote", "get-url", remote_name])
    if res.returncode == 0:
        set_res = _run_git(task_id, ["remote", "set-url", remote_name, remote_url])
        return set_res.returncode == 0
    else:
        add_res = _run_git(task_id, ["remote", "add", remote_name, remote_url])
        return add_res.returncode == 0

def has_remote(task_id: str, remote_name: str = "origin") -> bool:
    """Checks if the specified remote exists strictly in the isolated task workspace repository."""
    res = _run_git(task_id, ["remote", "get-url", remote_name])
    return res.returncode == 0

def git_push(task_id: str, branch_name: str, remote: str = "origin") -> Dict[str, Any]:
    """Pushes the branch from the isolated task workspace repository to remote."""
    res = _run_git(task_id, ["push", "-u", remote, branch_name])
    return {
        "success": res.returncode == 0,
        "stdout": _sanitize_git_output(res.stdout),
        "stderr": _sanitize_git_output(res.stderr),
        "returncode": res.returncode
    }
