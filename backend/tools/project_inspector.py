"""Repository-aware project inspection helpers for Nexus.

The inspector is deliberately read-only: it inventories a workspace and identifies
common project frameworks without executing repository code.
"""
from __future__ import annotations

import json
from pathlib import PurePosixPath
from typing import Any, Dict, List, Optional

from backend.tools.filesystem import list_files, read_file

MANIFESTS = (
    "package.json", "pyproject.toml", "requirements.txt", "Pipfile",
    "Cargo.toml", "go.mod", "pubspec.yaml", "pom.xml", "build.gradle",
    "build.gradle.kts", "Gemfile",
)
IGNORED_PREFIXES = (".git/", "node_modules/", ".next/", ".venv/", "venv/", "__pycache__/")


def _read_manifest(task_id: str, files: List[str], name: str) -> str:
    if name not in files:
        return ""
    try:
        return read_file(task_id, name)[:12000]
    except (OSError, ValueError):
        return ""


def detect_project_stack(files: List[str], manifests: Dict[str, str]) -> Dict[str, Any]:
    """Infer likely languages, frameworks and targets from manifests and paths."""
    package: Dict[str, Any] = {}
    if manifests.get("package.json"):
        try:
            package = json.loads(manifests["package.json"])
        except (json.JSONDecodeError, TypeError):
            package = {}

    deps = {}
    deps.update(package.get("dependencies") or {})
    deps.update(package.get("devDependencies") or {})
    paths = set(files)
    stack: List[str] = []
    targets: List[str] = []

    if "next" in deps or any(p.startswith(("app/", "src/app/")) and p.endswith(("page.tsx", "page.jsx")) for p in files):
        stack.append("Next.js")
        targets.append("web")
    if "react" in deps and "Next.js" not in stack:
        stack.append("React")
        targets.append("web")
    if "vue" in deps:
        stack.append("Vue")
        targets.append("web")
    if "svelte" in deps:
        stack.append("Svelte")
        targets.append("web")
    if "vite" in deps:
        stack.append("Vite")
        targets.append("web")
    if "expo" in deps or "react-native" in deps:
        stack.append("React Native / Expo")
        targets.append("mobile")
    if "electron" in deps:
        stack.append("Electron")
        targets.append("desktop")
    if "pubspec.yaml" in paths:
        stack.append("Flutter / Dart")
        targets.append("mobile")
    if "pyproject.toml" in paths or "requirements.txt" in paths:
        stack.append("Python")
        targets.append("backend" if any(p.endswith(".py") for p in files) else "python")
        requirements = manifests.get("requirements.txt", "").lower()
        pyproject = manifests.get("pyproject.toml", "").lower()
        if "fastapi" in requirements or "fastapi" in pyproject:
            stack.append("FastAPI")
            targets.append("api")
        elif "django" in requirements or "django" in pyproject:
            stack.append("Django")
            targets.append("web")
        elif "flask" in requirements or "flask" in pyproject:
            stack.append("Flask")
            targets.append("web")
    if "Cargo.toml" in paths:
        stack.append("Rust")
    if "go.mod" in paths:
        stack.append("Go")
    if not stack and any(p.endswith(".html") for p in files):
        stack.extend(["HTML", "CSS", "JavaScript"])
        targets.append("web")
    if not stack:
        stack.append("Unknown / new project")

    return {
        "stack": " + ".join(dict.fromkeys(stack)),
        "targets": list(dict.fromkeys(targets)),
        "package_name": package.get("name"),
        "package_scripts": package.get("scripts") or {},
        "manifest_files": [name for name in MANIFESTS if name in paths],
    }


def inspect_project(task_id: str, max_files: int = 500) -> Dict[str, Any]:
    """Return a bounded, read-only inventory and stack profile for a task workspace."""
    discovered = list_files(task_id, ".")
    files = sorted(
        path for path in discovered
        if not path.startswith(IGNORED_PREFIXES)
        and not PurePosixPath(path).name.startswith(".env")
    )[:max_files]
    manifests = {name: _read_manifest(task_id, files, name) for name in MANIFESTS}
    profile = detect_project_stack(files, manifests)
    return {
        "file_count": len(discovered),
        "inspected_file_count": len(files),
        "files": files,
        "profile": profile,
    }
