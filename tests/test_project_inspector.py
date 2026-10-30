import json

from backend.tools.project_inspector import detect_project_stack


def test_detects_nextjs_and_scripts():
    profile = detect_project_stack(
        ["package.json", "app/page.tsx", "app/layout.tsx"],
        {"package.json": json.dumps({
            "name": "demo",
            "dependencies": {"next": "14.2.0", "react": "18.0.0"},
            "devDependencies": {},
            "scripts": {"dev": "next dev", "build": "next build"},
        })},
    )
    assert "Next.js" in profile["stack"]
    assert "web" in profile["targets"]
    assert profile["package_name"] == "demo"
    assert profile["package_scripts"]["build"] == "next build"


def test_detects_react_native_and_electron_targets():
    profile = detect_project_stack(
        ["package.json"],
        {"package.json": json.dumps({
            "dependencies": {"react-native": "0.74.0", "electron": "30.0.0"},
        })},
    )
    assert "mobile" in profile["targets"]
    assert "desktop" in profile["targets"]


def test_detects_fastapi_from_requirements():
    profile = detect_project_stack(
        ["requirements.txt", "main.py"],
        {"requirements.txt": "fastapi>=0.110\nuvicorn\n"},
    )
    assert "FastAPI" in profile["stack"]
    assert "api" in profile["targets"]


def test_unknown_project_is_explicit():
    profile = detect_project_stack(["README.md"], {})
    assert profile["stack"] == "Unknown / new project"
