import json
import logging
from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
from backend.tools.filesystem import list_files, read_file
from backend.database.database import SessionLocal
from backend.database.models import PRDDocument

logger = logging.getLogger("nexus.agent.prd")

# JSON schema description for LLM-generated PRDs
PRD_JSON_SCHEMA = """{
  "title": "string — concise feature title",
  "summary": "string — 2-3 sentence overview of what will be built and why",
  "user_stories": ["As a <role>, I want <goal> so that <benefit>", ...],
  "requirements": {
    "functional": ["FR-1: ...", "FR-2: ...", ...],
    "nonfunctional": ["NFR-1: Performance: ...", "NFR-2: Accessibility: ...", ...]
  },
  "acceptance_criteria": ["AC-1: Given <context>, when <action>, then <result>", ...],
  "definition_of_done": ["DOD-1: ...", ...],
  "edge_cases": ["EC-1: ...", ...],
  "assumptions": ["assumption 1", ...],
  "out_of_scope": ["item 1", ...]
}"""


def _validate_prd(data: Dict[str, Any]) -> bool:
    """Validates that a PRD dict has all required fields with non-empty values."""
    if not isinstance(data, dict):
        return False
    required_keys = ["title", "summary", "acceptance_criteria"]
    for key in required_keys:
        if not data.get(key):
            return False
    # Normalize nested requirements to flat list for backward compatibility
    reqs = data.get("requirements", [])
    if isinstance(reqs, dict):
        flat = reqs.get("functional", []) + reqs.get("nonfunctional", [])
        data["requirements"] = flat
    elif not isinstance(reqs, list):
        data["requirements"] = []
    # Ensure all list fields are actually lists
    for key in ["acceptance_criteria", "definition_of_done", "edge_cases",
                 "user_stories", "assumptions", "out_of_scope"]:
        if key in data and not isinstance(data[key], list):
            data[key] = [str(data[key])]
    return True


class PRDAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="prd_agent",
            role_description="Transforms user feature requests into structured Product Requirements Documents."
        )

    async def execute(self, task_id: str, feature_request: str) -> Dict[str, Any]:
        run_id = self.log_run_start(task_id, f"Feature Request: {feature_request}")
        await self.emit_progress(task_id, "working", "Analyzing feature request and repository file tree...")

        tool_calls: List[Dict[str, Any]] = []

        # 1. Tool call: list repository files
        try:
            files = list_files(task_id, ".")
        except Exception as e:
            logger.warning(f"Failed to list files for task {task_id}: {e}")
            files = []
        tool_calls.append({"tool": "list_files", "args": {"path": "."}, "result_count": len(files)})
        await self.emit_progress(task_id, "working", f"Discovered {len(files)} files in repository")

        # 2. Tool call: read key files for context if available
        repo_context = ""
        context_files = ["README.md", "package.json", "index.html", "App.tsx",
                         "main.py", "app.py", "tsconfig.json", "requirements.txt"]
        for key_file in context_files:
            if key_file in files:
                try:
                    content = read_file(task_id, key_file)
                    tool_calls.append({"tool": "read_file", "args": {"path": key_file}})
                    repo_context += f"\n--- {key_file} ---\n" + content[:2000]
                except Exception:
                    pass

        await self.emit_progress(task_id, "working", "Synthesizing product requirements & acceptance criteria...")

        prd_data: Dict[str, Any] = {}
        if self.client:
            try:
                system_prompt = (
                    "You are the Lead PRD Agent in the Nexus Autonomous Software Engineering Team.\n"
                    "Your job is to generate a comprehensive Product Requirements Document (PRD) in JSON format.\n\n"
                    "Guidelines:\n"
                    "- Analyze the feature request and existing codebase context to produce precise, actionable requirements.\n"
                    "- Write user stories in 'As a <role>, I want <goal> so that <benefit>' format.\n"
                    "- Separate functional and nonfunctional requirements (performance, accessibility, security).\n"
                    "- Write acceptance criteria in 'Given/When/Then' format where possible.\n"
                    "- Identify assumptions and items explicitly out of scope.\n"
                    "- Do NOT invent requirements the user never requested.\n"
                    "- Do NOT propose altering existing core architecture unnecessarily.\n"
                    "- If the request is ambiguous, note assumptions rather than guessing.\n\n"
                    f"Output strictly valid JSON matching this schema:\n{PRD_JSON_SCHEMA}"
                )
                user_prompt = (
                    f"Feature Request:\n{feature_request}\n\n"
                    f"Repository Files ({len(files)} total):\n{files[:50]}\n\n"
                    f"Repository Context:\n{repo_context}"
                )
                prd_data = self.call_llm_json(system_prompt, user_prompt)
                if not _validate_prd(prd_data):
                    logger.warning(f"LLM PRD output failed validation for task {task_id}")
                    prd_data = {}
            except Exception as e:
                logger.error(f"LLM error in PRD agent for task {task_id}: {e}")
                await self.emit_progress(task_id, "working", f"LLM error: {str(e)}. Falling back to deterministic synthesizer.")

        if not prd_data or not prd_data.get("title"):
            prd_data = self._synthesize_prd(feature_request, files)

        # Ensure backward-compatible flat requirements list for DB storage
        reqs_for_db = prd_data.get("requirements", [])
        if isinstance(reqs_for_db, dict):
            reqs_for_db = reqs_for_db.get("functional", []) + reqs_for_db.get("nonfunctional", [])

        # Save to database
        db = SessionLocal()
        try:
            doc = PRDDocument(
                task_id=task_id,
                title=prd_data["title"],
                summary=prd_data["summary"],
                requirements=json.dumps(reqs_for_db),
                acceptance_criteria=json.dumps(prd_data.get("acceptance_criteria", [])),
                definition_of_done=json.dumps(prd_data.get("definition_of_done", [])),
                edge_cases=json.dumps(prd_data.get("edge_cases", [])),
                approved=False
            )
            db.add(doc)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to save PRD to database for task {task_id}: {e}")
            db.rollback()
            raise
        finally:
            db.close()

        self.log_run_complete(run_id, f"Generated PRD: {prd_data['title']}", tool_calls=tool_calls)
        await self.emit_progress(task_id, "completed", f"PRD generated: '{prd_data['title']}'", data={"prd": prd_data})
        return prd_data

    def _synthesize_prd(self, feature_request: str, files: List[str]) -> Dict[str, Any]:
        """Deterministic fallback PRD synthesizer when LLM is unavailable."""
        title = f"PRD: {feature_request[:60]}"
        req_lower = feature_request.lower()

        if any(k in req_lower for k in ["contact", "form", "message", "email", "submit", "inquiry"]):
            user_stories = [
                "As a visitor, I want a contact form so that I can send inquiries to the site owner",
                "As a visitor, I want validation feedback so that I know my submission was received"
            ]
            reqs = [
                "FR-1: Add a dedicated responsive contact section with name, email, message textarea, and submit button",
                "FR-2: Validate required fields (name, valid email format, non-empty message body)",
                "FR-3: Provide immediate user feedback on form submission with clear success status",
                "NFR-1: Responsive layout adapts cleanly across mobile viewports (375px+) and desktop",
                "NFR-2: Form submit button must have minimum 44px touch target on mobile"
            ]
            ac = [
                "AC-1: Given the contact page loads, then name/email/message inputs and submit button are visible",
                "AC-2: Given valid input in all fields, when submit is clicked, then a success message appears",
                "AC-3: Given an empty required field, when submit is clicked, then browser validation prevents submission",
                "AC-4: Given a 375px mobile viewport, then all form elements remain visible without horizontal scroll"
            ]
            edge_cases = [
                "EC-1: Submission with empty or whitespace-only fields",
                "EC-2: Invalid email string formatting (missing @, domain)",
                "EC-3: Very long input text (>5000 chars) in message field",
                "EC-4: Mobile viewport resizing (375px to 1280px) preserving form layout"
            ]
        elif "wishlist" in req_lower:
            user_stories = [
                "As a shopper, I want to add products to a wishlist so that I can save items for later",
                "As a shopper, I want to see my wishlist count so that I know how many items I've saved"
            ]
            reqs = [
                "FR-1: Implement user-facing wishlist toggle button for each product card",
                "FR-2: Maintain a live counter badge showing total wishlisted items",
                "FR-3: Toggle state persists during the session with visual indication (filled/unfilled heart)",
                "NFR-1: Responsive viewport display including mobile screen widths (375px+)",
                "NFR-2: Toggle interaction should respond within 100ms"
            ]
            ac = [
                "AC-1: Given a product card, then a wishlist toggle button is visible",
                "AC-2: Given the button is clicked, then the item is added and counter increments",
                "AC-3: Given the button is clicked again, then the item is removed and counter decrements",
                "AC-4: Given a 375px mobile viewport, then wishlist controls remain visible and operable"
            ]
            edge_cases = [
                "EC-1: Rapid consecutive clicking on interaction buttons",
                "EC-2: Viewport resizing between desktop (1280px) and mobile (375px)",
                "EC-3: Handling empty state when no items are selected (counter shows 0)"
            ]
        else:
            user_stories = [
                f"As a user, I want {feature_request.lower()[:80]} so that my experience is improved"
            ]
            reqs = [
                f"FR-1: Implement user-facing functionality for: {feature_request}",
                "FR-2: Maintain seamless integration with existing UI components and responsive styling",
                "FR-3: Ensure interactive state updates smoothly upon user interaction",
                "NFR-1: Support responsive viewport display including mobile screen widths (375px+)",
                "NFR-2: No console errors or layout regressions introduced"
            ]
            ac = [
                f"AC-1: Feature controls for '{feature_request[:40]}' are visible and interactive",
                "AC-2: User interaction triggers appropriate responsive feedback",
                "AC-3: Controls remain fully visible and usable on mobile viewports without horizontal clipping",
                "AC-4: Application loads cleanly without console errors or layout breaks"
            ]
            edge_cases = [
                "EC-1: Rapid consecutive user interactions",
                "EC-2: Viewport resizing between desktop (1280px) and mobile (375px)",
                "EC-3: Handling empty or boundary input states"
            ]

        return {
            "title": title,
            "summary": f"Specification to implement: {feature_request}. Seamlessly integrate functionality into the existing application with responsive design and state persistence.",
            "user_stories": user_stories,
            "requirements": reqs,
            "acceptance_criteria": ac,
            "definition_of_done": [
                "DOD-1: Code implemented strictly within repository architecture",
                "DOD-2: Browser automation tests pass for desktop and mobile viewports",
                "DOD-3: No visual regressions introduced to existing layout",
                "DOD-4: All code formatted and ready for pull request"
            ],
            "edge_cases": edge_cases,
            "assumptions": [
                "The target repository has a standard HTML/JS/CSS or framework-based structure",
                "No backend API changes are required unless explicitly requested"
            ],
            "out_of_scope": [
                "Server-side data persistence (unless explicitly requested)",
                "Authentication and authorization changes",
                "Third-party service integrations not mentioned in the request"
            ]
        }

prd_agent = PRDAgent()
