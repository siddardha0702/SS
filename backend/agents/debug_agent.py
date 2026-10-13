import json
import logging
from typing import Dict, Any, List
from backend.agents.base_agent import BaseAgent
from backend.tools.filesystem import read_file, search_code
from backend.database.database import SessionLocal
from backend.database.models import DebugReport

logger = logging.getLogger("nexus.agent.debug")

DEBUG_JSON_SCHEMA = """{
  "failure_type": "ui_visibility | logic_error | selector_mismatch | state_error | network_error",
  "root_cause": "string — concise description of the root cause",
  "affected_files": ["path/to/file1", ...],
  "explanation": "string — detailed technical explanation of why the test failed",
  "fix_plan": [
    "Step 1: Locate ...",
    "Step 2: Modify ...",
    "Step 3: Verify ..."
  ],
  "severity": "low | medium | high | critical"
}"""


def _validate_debug_report(data: Dict[str, Any]) -> bool:
    """Validates debug report schema and normalizes fields."""
    if not isinstance(data, dict):
        return False
    if not data.get("root_cause") or not data.get("explanation"):
        return False
    if not isinstance(data.get("affected_files"), list):
        data["affected_files"] = [str(data.get("affected_files", ""))]
    if not isinstance(data.get("fix_plan"), list):
        data["fix_plan"] = [str(data.get("fix_plan", ""))]
    if data.get("severity") not in ["low", "medium", "high", "critical"]:
        data["severity"] = "medium"
    return True


class DebugAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="debug_agent",
            role_description="Analyzes test failures, traces root causes in source code, and devises surgical fix plans."
        )

    async def execute(
        self,
        task_id: str,
        test_results: Dict[str, Any],
        prd_data: Dict[str, Any],
        arch_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        failures = test_results.get("failures", [])
        run_id = self.log_run_start(task_id, f"Analyzing {len(failures)} test failures")
        await self.emit_progress(task_id, "working", "Analyzing test logs, browser traces, and source code...")

        tool_calls: List[Dict[str, Any]] = []

        target_file = arch_data.get("files_to_modify", ["index.html"])[0]
        code_content = ""
        try:
            code_content = read_file(task_id, target_file)
            tool_calls.append({"tool": "read_file", "args": {"path": target_file}})
        except Exception as e:
            logger.warning(f"Failed to read target file {target_file} for debug analysis: {e}")

        # Search code for elements mentioned in failure messages
        search_hits = []
        for fail_msg in failures[:3]:
            # Extract possible selector or keyword
            words = [w for w in fail_msg.replace("(", " ").replace(")", " ").split() if len(w) > 4 and not w.startswith("http")]
            for word in words[:2]:
                try:
                    hits = search_code(task_id, word)
                    if hits:
                        search_hits.extend(hits[:3])
                        tool_calls.append({"tool": "search_code", "args": {"query": word}, "hits": len(hits)})
                except Exception:
                    pass

        debug_data: Dict[str, Any] = {}

        if self.client:
            try:
                system_prompt = (
                    "You are the Lead Debug Agent in the Nexus Autonomous Software Engineering Team.\n"
                    "Analyze the automated test failures, inspect the source code, and provide a precise root cause analysis.\n"
                    "Requirements:\n"
                    "- Categorize the failure type precisely.\n"
                    "- Pinpoint the exact line or markup causing the failure.\n"
                    "- Provide surgical, step-by-step fix instructions for the Developer Agent.\n"
                    "- Do NOT propose rewriting the entire project. Focus exclusively on the bug.\n\n"
                    f"Output strictly valid JSON matching this schema:\n{DEBUG_JSON_SCHEMA}"
                )
                user_prompt = (
                    f"Test Failures:\n{json.dumps(failures, indent=2)}\n\n"
                    f"Test Requirements and Results:\n{json.dumps(test_results.get('requirements', []), indent=2)}\n\n"
                    f"PRD Summary:\n{prd_data.get('summary', '')}\n\n"
                    f"Target File ({target_file}) Snippet:\n{code_content[:3000]}\n\n"
                    f"Code Search Hits:\n{json.dumps(search_hits, indent=2)}"
                )
                debug_data = self.call_llm_json(system_prompt, user_prompt)
                if not _validate_debug_report(debug_data):
                    logger.warning(f"LLM debug output failed validation for task {task_id}")
                    debug_data = {}
            except Exception as e:
                logger.error(f"LLM error in debug agent for task {task_id}: {e}")
                await self.emit_progress(task_id, "working", f"LLM error: {str(e)}. Using root cause analysis engine.")

        if not debug_data or not debug_data.get("root_cause"):
            debug_data = self._diagnose_failures(failures, code_content, target_file)

        # Save to database
        db = SessionLocal()
        try:
            report = DebugReport(
                task_id=task_id,
                root_cause=debug_data["root_cause"],
                affected_files=json.dumps(debug_data["affected_files"]),
                explanation=debug_data["explanation"],
                fix_plan=json.dumps(debug_data["fix_plan"]),
                severity=debug_data.get("severity", "medium")
            )
            db.add(report)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to save DebugReport to database for task {task_id}: {e}")
            db.rollback()
            raise
        finally:
            db.close()

        self.log_run_complete(run_id, f"Root cause diagnosed: {debug_data['root_cause'][:60]}", tool_calls=tool_calls)
        await self.emit_progress(
            task_id,
            "completed",
            f"Root cause identified: {debug_data['root_cause']}",
            data={"debug_report": debug_data}
        )
        return debug_data

    def _diagnose_failures(self, failures: List[str], code_content: str, target_file: str) -> Dict[str, Any]:
        """Deterministic root cause analysis engine when LLM is unavailable."""
        fail_text = " ".join(failures).lower()

        # Scenario A: Responsive visibility limitation on mobile
        if any("hidden md:" in code_content for _ in [1]) or any(k in fail_text for k in ["mobile", "375px", "viewport", "hidden", "inaccessible"]):
            is_contact = any(k in code_content.lower() for k in ["contact-form", "contact-submit-btn"])
            elem_name = "Contact submit button (#contact-submit-btn)" if is_contact else "Feature UI control"
            return {
                "failure_type": "ui_visibility",
                "root_cause": f"{elem_name} contains responsive visibility constraint 'hidden md:...', suppressing rendering on mobile screens narrower than 768px.",
                "affected_files": [target_file],
                "explanation": (
                    "The Tailwind utility class 'hidden' hides the element by default at mobile screen widths (375px), "
                    "while 'md:inline-flex' or 'md:block' only restores display on medium screens (768px+) and above. "
                    "When the automated Playwright test suite simulated a 375px mobile viewport, the element was not rendered or visible."
                ),
                "fix_plan": [
                    f"Locate the responsive element markup inside '{target_file}'",
                    "Remove the 'hidden md:' prefix constraint from class attributes",
                    "Ensure 'inline-flex' or 'flex' or 'block' applies universally across both mobile and desktop viewports",
                    "Verify touch target sizing and spacing for mobile usability"
                ],
                "severity": "medium"
            }

        # Scenario B: Missing selector / element not found
        if any(k in fail_text for k in ["not found", "missing", "selector"]):
            return {
                "failure_type": "selector_mismatch",
                "root_cause": f"Expected element selector was not located in '{target_file}': {failures[0] if failures else 'Missing element'}",
                "affected_files": [target_file],
                "explanation": "The test assertion looked for a specific class or ID selector that was either omitted from the template or mismatched with the implementation.",
                "fix_plan": [
                    f"Inspect the DOM structure of '{target_file}'",
                    "Add or correct the missing selector/ID attribute on the target component",
                    "Ensure the component is rendered within the primary DOM hierarchy"
                ],
                "severity": "high"
            }

        # Scenario C: State / interaction failure
        if any(k in fail_text for k in ["counter", "badge", "click", "increment", "state"]):
            return {
                "failure_type": "state_error",
                "root_cause": f"Interactive state handler failed to update UI on click: {failures[0] if failures else 'State error'}",
                "affected_files": [target_file],
                "explanation": "Click event listener did not properly mutate reactive state store or update the corresponding badge counter in the DOM.",
                "fix_plan": [
                    "Inspect click event listener and state management script",
                    "Ensure DOM element exists before attempting to update textContent / innerText",
                    "Verify state changes persist across interactions"
                ],
                "severity": "medium"
            }

        # Generic failure fallback
        return {
            "failure_type": "logic_error",
            "root_cause": f"Observed failure during test execution: {failures[0] if failures else 'Element assertion failed'}",
            "affected_files": [target_file],
            "explanation": "The target component or handler did not satisfy the expected assertion criterion during automated testing.",
            "fix_plan": [
                f"Examine component rendering logic in '{target_file}'",
                "Ensure required CSS, selectors, and event handlers match test criteria",
                "Re-execute test suite to verify resolution"
            ],
            "severity": "medium"
        }

debug_agent = DebugAgent()
