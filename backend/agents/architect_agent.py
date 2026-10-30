import json
import logging
from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
from backend.tools.filesystem import list_files, read_file
from backend.tools.project_inspector import inspect_project
from backend.database.database import SessionLocal
from backend.database.models import Architecture

logger = logging.getLogger("nexus.agent.architect")

ARCH_JSON_SCHEMA = """{
  "summary": "string — high-level technical approach",
  "tech_stack": "string — detected tech stack (e.g. React, Next.js, HTML/Tailwind, FastAPI)",
  "architecture": "string — detailed component hierarchy, state flow, and design patterns",
  "files_to_modify": ["path/to/file1", ...],
  "files_to_create": ["path/to/new_file", ...],
  "dependencies": ["dependency-name (if needed, otherwise empty)"],
  "implementation_steps": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ],
  "risks": [
    "Risk 1 with mitigation",
    "Risk 2 with mitigation"
  ],
  "backward_compatibility": "string — notes on preserving existing functionality"
}"""


def _detect_tech_stack(files: List[str], repo_context: Dict[str, str]) -> str:
    """Detects primary framework and styling system from discovered files."""
    if "package.json" in repo_context:
        pkg = repo_context["package.json"].lower()
        if "next" in pkg:
            return "Next.js + React"
        if "react" in pkg:
            return "React (SPA)"
        if "vue" in pkg:
            return "Vue.js"
    if any(f.endswith((".tsx", ".jsx")) for f in files):
        return "React / TypeScript"
    if any(f.endswith(".html") for f in files):
        if any("tailwind" in repo_context.get(f, "").lower() for f in repo_context):
            return "HTML5 + Tailwind CSS"
        return "HTML5 / JavaScript"
    if any(f.endswith(".py") for f in files):
        return "Python"
    return "Web Application"


def _validate_architecture(data: Dict[str, Any]) -> bool:
    """Validates architecture data schema."""
    if not isinstance(data, dict):
        return False
    if not data.get("summary") or not data.get("architecture"):
        return False
    if not isinstance(data.get("files_to_modify"), list):
        data["files_to_modify"] = [str(data.get("files_to_modify", "index.html"))]
    if not isinstance(data.get("files_to_create"), list):
        data["files_to_create"] = []
    if not isinstance(data.get("dependencies"), list):
        data["dependencies"] = []
    if not isinstance(data.get("implementation_steps"), list):
        data["implementation_steps"] = [str(data.get("implementation_steps", ""))]
    if not isinstance(data.get("risks"), list):
        data["risks"] = []
    return True


class ArchitectAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="architect_agent",
            role_description="Analyzes repository structure, dependencies, and creates the technical architecture specification."
        )

    async def execute(self, task_id: str, prd_data: Dict[str, Any]) -> Dict[str, Any]:
        run_id = self.log_run_start(task_id, f"PRD: {prd_data.get('title', 'Feature PRD')}")
        await self.emit_progress(task_id, "working", "Inspecting repository codebase, file tree, and module dependencies...")

        tool_calls: List[Dict[str, Any]] = []

        # 1. Tool call: list repository files
        try:
            files = list_files(task_id, ".")
        except Exception as e:
            logger.warning(f"Failed to list files for task {task_id}: {e}")
            files = []
        tool_calls.append({"tool": "list_files", "args": {"path": "."}, "result_count": len(files)})

        # 2. Inspect key configuration and entry-point files
        file_samples: Dict[str, str] = {}
        priority_files = [
            "package.json", "index.html", "src/App.tsx", "src/App.jsx", "src/index.tsx",
            "app/page.tsx", "app/layout.tsx", "pages/index.tsx", "main.py", "app.py",
            "README.md", "tailwind.config.js"
        ]
        # Inspect priority files that exist
        for pf in priority_files:
            if pf in files:
                try:
                    content = read_file(task_id, pf)
                    tool_calls.append({"tool": "read_file", "args": {"path": pf}})
                    file_samples[pf] = content[:1500]
                except Exception:
                    pass

        # Also inspect up to 5 other code files
        for f in files:
            if len(file_samples) >= 8:
                break
            if f not in file_samples and f.endswith((".html", ".js", ".ts", ".tsx", ".py", ".css")):
                try:
                    content = read_file(task_id, f)
                    tool_calls.append({"tool": "read_file", "args": {"path": f}})
                    file_samples[f] = content[:1000]
                except Exception:
                    pass

        project_profile = inspect_project(task_id)
        tech_stack = project_profile.get("profile", {}).get("stack") or _detect_tech_stack(files, file_samples)
        await self.emit_progress(task_id, "working", f"Detected tech stack: {tech_stack}. Designing architecture...")

        arch_data: Dict[str, Any] = {}
        if self.client:
            try:
                system_prompt = (
                    "You are the Software Architect Agent in the Nexus Autonomous Software Engineering Team.\n"
                    "Analyze the approved PRD and existing codebase to output a technical architecture blueprint in JSON.\n\n"
                    "Requirements:\n"
                    "- Carefully inspect the repository files, component structure, and styling.\n"
                    "- Choose files_to_modify and files_to_create that exist or make sense in the repository.\n"
                    "- Define component hierarchy, reactive state management, and event flow.\n"
                    "- Identify precise implementation steps in execution order.\n"
                    "- Call out architectural risks (layout shifts, performance, accessibility) with mitigations.\n"
                    "- Emphasize backward compatibility and preserving existing user code.\n"
                    "- Do NOT propose unnecessary rewrites or adding heavy external dependencies.\n\n"
                    f"Output strictly valid JSON matching this schema:\n{ARCH_JSON_SCHEMA}"
                )
                user_prompt = (
                    f"Approved PRD:\n{json.dumps(prd_data, indent=2)}\n\n"
                    f"Detected Tech Stack: {tech_stack}\n"
                    f"Project Profile: {json.dumps(project_profile.get('profile', {}), indent=2)}\n"
                    f"Repository Files ({len(files)} total):\n{files[:50]}\n\n"
                    f"File Samples:\n{json.dumps(file_samples, indent=2)}"
                )
                arch_data = self.call_llm_json(system_prompt, user_prompt)
                if not _validate_architecture(arch_data):
                    logger.warning(f"LLM architecture output failed validation for task {task_id}")
                    arch_data = {}
            except Exception as e:
                logger.error(f"LLM error in architect agent for task {task_id}: {e}")
                await self.emit_progress(task_id, "working", f"LLM error: {str(e)}. Using deterministic architecture synthesis.")

        if not arch_data or not arch_data.get("summary"):
            arch_data = self._synthesize_architecture(prd_data, files, tech_stack)

        # Save to database
        db = SessionLocal()
        try:
            doc = Architecture(
                task_id=task_id,
                summary=arch_data["summary"],
                architecture=arch_data["architecture"],
                files_to_modify=json.dumps(arch_data["files_to_modify"]),
                files_to_create=json.dumps(arch_data.get("files_to_create", [])),
                dependencies=json.dumps(arch_data.get("dependencies", [])),
                implementation_steps=json.dumps(arch_data["implementation_steps"]),
                risks=json.dumps(arch_data.get("risks", [])),
                approved=False
            )
            db.add(doc)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to save Architecture to database for task {task_id}: {e}")
            db.rollback()
            raise
        finally:
            db.close()

        self.log_run_complete(run_id, f"Architecture blueprint created: {arch_data['summary'][:60]}", tool_calls=tool_calls)
        await self.emit_progress(task_id, "completed", "Architecture blueprint finalized and ready for user review.", data={"architecture": arch_data})
        return arch_data

    def _synthesize_architecture(self, prd_data: Dict[str, Any], files: List[str], tech_stack: str) -> Dict[str, Any]:
        """Deterministic fallback architecture synthesizer when LLM is unavailable."""
        # Find the primary target file
        candidate_files = ["index.html", "src/App.tsx", "src/App.jsx", "app/page.tsx", "src/index.html"]
        target_file = "index.html"
        for cand in candidate_files:
            if cand in files:
                target_file = cand
                break
        if target_file not in files and files:
            for f in files:
                if f.endswith((".html", ".tsx", ".jsx", ".js")):
                    target_file = f
                    break

        prd_text = (prd_data.get("title", "") + " " + prd_data.get("summary", "")).lower()

        if any(k in prd_text for k in ["contact", "form", "message", "email", "submit", "inquiry"]):
            return {
                "summary": f"Modular contact section component integrated into {target_file} with responsive form layout, client validation, and submission feedback.",
                "tech_stack": tech_stack,
                "architecture": (
                    "1. UI Layer: Render a dedicated, responsive contact section containing input fields (name, email), a message textarea, and a styled submit button.\n"
                    "2. State Layer: Handle client-side form submission event, prevent default navigation, validate entries, and show an inline success feedback alert.\n"
                    "3. Style Layer: Use responsive Tailwind CSS utilities (w-full, grid/flex, rounded, dark theme matching background) ensuring full visibility on mobile (375px) and desktop."
                ),
                "files_to_modify": [target_file],
                "files_to_create": [],
                "dependencies": [],
                "implementation_steps": [
                    f"Locate main content container in {target_file}",
                    "Append a responsive contact section with name, email, message textarea, and submit button",
                    "Attach JavaScript form submission handler with validation and success banner display",
                    "Ensure responsive viewport styling adapts cleanly across mobile (375px) and desktop (1280px)"
                ],
                "risks": [
                    "Input element overflow on narrow viewports if fixed width rather than w-full is applied. Mitigation: use w-full with max-w container.",
                    "Missing submit button on mobile if breakpoint hiding classes are used. Mitigation: ensure universal visibility."
                ],
                "backward_compatibility": "Preserves all existing page sections, navigation, and script tags without disruption."
            }
        elif "wishlist" in prd_text:
            return {
                "summary": f"Modular implementation integrating requested feature directly into {target_file} with responsive component styling and isolated state management.",
                "tech_stack": tech_stack,
                "architecture": (
                    "1. UI Layer: Mount feature controls directly onto each product item with dedicated action handlers.\n"
                    "2. State Layer: Maintain an interactive reactive state store (e.g. Set/Array of active item IDs) with counter badge sync.\n"
                    "3. Style Layer: Apply mobile-responsive Tailwind/CSS flexbox utilities ensuring visibility on all viewports without horizontal scroll."
                ),
                "files_to_modify": [target_file],
                "files_to_create": [],
                "dependencies": [],
                "implementation_steps": [
                    f"Inspect existing layout and item template in {target_file}",
                    "Add interactive state tracker and toggle event handlers",
                    "Add action button to product item template with appropriate SVG/icon and badge counter",
                    "Ensure responsive layout rules apply across desktop (1280px) and mobile (375px)"
                ],
                "risks": [
                    "Button overflow or overlapping on narrow screen widths if CSS flex properties are not configured responsively. Mitigation: use responsive flexbox utilities.",
                    "State loss on page refresh. Mitigation: state lives in session memory or localStorage."
                ],
                "backward_compatibility": "Augments existing product cards with action button while leaving catalog rendering untouched."
            }
        else:
            return {
                "summary": f"Modular implementation integrating requested feature directly into {target_file} with responsive component styling.",
                "tech_stack": tech_stack,
                "architecture": (
                    f"1. UI Layer: Add user-facing feature interface to {target_file}.\n"
                    "2. State Layer: Maintain reactive state handlers for user interactions.\n"
                    "3. Style Layer: Apply mobile-responsive Tailwind utilities ensuring seamless display on all screen widths."
                ),
                "files_to_modify": [target_file],
                "files_to_create": [],
                "dependencies": [],
                "implementation_steps": [
                    f"Inspect existing layout in {target_file}",
                    "Integrate requested UI elements and state handlers",
                    "Verify mobile (375px) and desktop (1280px) responsiveness"
                ],
                "risks": [
                    "Potential layout shift on mobile viewports if width constraints are omitted. Mitigation: apply responsive layout classes."
                ],
                "backward_compatibility": "All existing components, routes, and data flows remain unmodified."
            }

architect_agent = ArchitectAgent()

