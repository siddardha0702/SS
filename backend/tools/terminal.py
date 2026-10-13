import re
import logging
from typing import Dict, Any
from backend.workspace.docker_manager import docker_manager

logger = logging.getLogger("nexus.tools.terminal")

# Allowed command binaries for workspace execution
ALLOWED_COMMANDS = {
    "npm", "npx", "node", "python", "py", "pip", "pytest", "git",
    "ls", "dir", "cat", "type", "echo", "mkdir", "cp", "mv",
    "tsc", "eslint", "prettier", "find", "grep"
}

def _validate_command(command: str) -> str:
    """
    Validates that command uses an allowed binary.
    Rejects dangerous shell metacharacters chained with unauthorized commands.
    """
    stripped = command.strip()
    if not stripped:
        raise ValueError("Empty command cannot be executed.")

    # Check the base executable
    first_token = stripped.split()[0].replace('"', '').replace("'", "")
    base_cmd = first_token.split("/")[-1].split("\\")[-1].lower()
    base_cmd = re.sub(r'\.(exe|cmd|bat)$', '', base_cmd)

    if base_cmd not in ALLOWED_COMMANDS:
        raise ValueError(
            f"Security violation: Command binary '{base_cmd}' is not in the authorized tool allowlist: "
            f"{sorted(list(ALLOWED_COMMANDS))}"
        )
    return stripped

def _sanitize_package_name(package: str) -> str:
    """Validates package name format to prevent shell argument injection."""
    cleaned = package.strip()
    if not re.match(r'^[a-zA-Z0-9@_./^~<>=! -]+$', cleaned):
        raise ValueError(f"Invalid package identifier: '{cleaned}' contains forbidden characters.")
    return cleaned

def run_command(task_id: str, command: str, timeout: int = 60) -> Dict[str, Any]:
    """Runs a validated, sandboxed command inside the task's repository folder."""
    try:
        valid_cmd = _validate_command(command)
    except ValueError as e:
        logger.warning(f"Rejected command for task {task_id}: {e}")
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "success": False
        }
    return docker_manager.run_command(task_id=task_id, command=valid_cmd, cwd_subpath="repository", timeout=timeout)

def install_dependency(task_id: str, package: str, package_manager: str = "npm") -> Dict[str, Any]:
    """Installs a dependency safely in the task workspace."""
    try:
        safe_pkg = _sanitize_package_name(package)
    except ValueError as e:
        return {"returncode": -1, "stdout": "", "stderr": str(e), "success": False}

    mgr = package_manager.lower().strip()
    if mgr == "npm":
        cmd = f"npm install {safe_pkg}"
    elif mgr == "pip":
        cmd = f"pip install {safe_pkg}"
    else:
        return {"returncode": -1, "stdout": "", "stderr": f"Unsupported package manager: {mgr}", "success": False}

    return run_command(task_id, cmd, timeout=120)
