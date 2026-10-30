import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from backend.config import settings
from backend.orchestrator.state import TaskState, AgentName
from backend.orchestrator.events import manager
from backend.database.database import SessionLocal
from backend.database.models import Task, PRDDocument, Architecture, PullRequest, AgentRun
from backend.workspace.docker_manager import docker_manager
from backend.agents.prd_agent import prd_agent
from backend.agents.architect_agent import architect_agent
from backend.agents.developer_agent import developer_agent
from backend.agents.tester_agent import tester_agent
from backend.agents.debug_agent import debug_agent
from backend.agents.reviewer_agent import reviewer_agent
from backend.tools.github import create_pull_request, parse_github_repo
from backend.tools.git import git_push, setup_remote

logger = logging.getLogger("nexus.orchestrator")

class NexusOrchestrator:
    def __init__(self):
        self.max_retries = settings.MAX_RETRIES

    def _update_task_state(self, task_id: str, state: TaskState, current_agent: Optional[str] = None, error: Optional[str] = None):
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = state.value
                task.current_agent = current_agent
                if error:
                    task.error_message = error
                db.commit()
        finally:
            db.close()

    def _is_cancelled(self, task_id: str) -> bool:
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            return task is None or task.status == TaskState.CANCELLED.value
        finally:
            db.close()

    async def start_task(self, task_id: str):
        """Initializes workspace and kicks off PRD generation."""
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return
            feature_request = task.feature_request
            repo_source = task.repository
            branch_name = f"nexus/task-{task_id[:8]}"
            task.branch_name = branch_name
            db.commit()
        finally:
            db.close()

        # Step 1: Workspace creation
        self._update_task_state(task_id, TaskState.WORKSPACE_CREATING)
        await manager.broadcast(task_id, "orchestrator", "working", "Setting up isolated task workspace sandbox...")
        try:
            paths = docker_manager.setup_workspace(task_id, repo_source)
            await manager.broadcast(task_id, "orchestrator", "working", f"Workspace established at {paths['task_dir']}")
        except Exception as e:
            self._update_task_state(task_id, TaskState.PRD_FAILED, error=str(e))
            await manager.broadcast(task_id, "orchestrator", "failed", f"Failed to initialize workspace: {str(e)}")
            return

        # Step 2: PRD Generation
        self._update_task_state(task_id, TaskState.PRD_GENERATING, current_agent=AgentName.PRD.value)
        try:
            prd_data = await prd_agent.execute(task_id, feature_request)
            self._update_task_state(task_id, TaskState.PRD_PENDING_APPROVAL, current_agent=None)
            await manager.broadcast(
                task_id,
                "orchestrator",
                "waiting_for_approval",
                "PRD generated successfully. Awaiting User Approval (Gate 1).",
                data={"prd": prd_data}
            )
        except Exception as e:
            self._update_task_state(task_id, TaskState.PRD_FAILED, error=str(e))
            await manager.broadcast(task_id, "orchestrator", "failed", f"PRD Agent failed: {str(e)}")

    async def approve_prd(self, task_id: str):
        """Human Gate 1 Approved: Transitions to Architecture Generation."""
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return
            prd_doc = db.query(PRDDocument).filter(PRDDocument.task_id == task_id).order_by(PRDDocument.created_at.desc()).first()
            if prd_doc:
                prd_doc.approved = True
                db.commit()
                prd_data = {
                    "title": prd_doc.title,
                    "summary": prd_doc.summary,
                    "requirements": json.loads(prd_doc.requirements),
                    "acceptance_criteria": json.loads(prd_doc.acceptance_criteria),
                    "definition_of_done": json.loads(prd_doc.definition_of_done),
                    "edge_cases": json.loads(prd_doc.edge_cases) if prd_doc.edge_cases else []
                }
            else:
                prd_data = {"title": "Approved PRD", "requirements": []}
        finally:
            db.close()

        self._update_task_state(task_id, TaskState.ARCHITECTURE_GENERATING, current_agent=AgentName.ARCHITECT.value)
        await manager.broadcast(task_id, "orchestrator", "working", "PRD Approved by user. Architect Agent starting...")

        try:
            arch_data = await architect_agent.execute(task_id, prd_data)
            self._update_task_state(task_id, TaskState.ARCHITECTURE_PENDING_APPROVAL, current_agent=None)
            await manager.broadcast(
                task_id,
                "orchestrator",
                "waiting_for_approval",
                "Architecture blueprint ready. Awaiting User Approval (Gate 2).",
                data={"architecture": arch_data}
            )
        except Exception as e:
            self._update_task_state(task_id, TaskState.ARCHITECTURE_FAILED, error=str(e))
            await manager.broadcast(task_id, "orchestrator", "failed", f"Architect Agent failed: {str(e)}")

    async def reject_prd(self, task_id: str, feedback: str):
        self._update_task_state(task_id, TaskState.PRD_FAILED, error=feedback)
        await manager.broadcast(task_id, "orchestrator", "rejected", f"PRD rejected by user: {feedback}")

    async def approve_architecture(self, task_id: str):
        """Human Gate 2 Approved: Transitions to Development -> Testing -> Self-Correction -> Review -> PR."""
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return
            branch_name = task.branch_name or f"nexus/task-{task_id[:8]}"
            repo_url = task.repository
            feature_request = task.feature_request

            prd_doc = db.query(PRDDocument).filter(PRDDocument.task_id == task_id).order_by(PRDDocument.created_at.desc()).first()
            arch_doc = db.query(Architecture).filter(Architecture.task_id == task_id).order_by(Architecture.created_at.desc()).first()
            if arch_doc:
                arch_doc.approved = True
                db.commit()

            prd_data = {
                "title": prd_doc.title if prd_doc else "Feature",
                "summary": prd_doc.summary if prd_doc else "",
                "requirements": json.loads(prd_doc.requirements) if prd_doc else [],
                "acceptance_criteria": json.loads(prd_doc.acceptance_criteria) if prd_doc else []
            }
            arch_data = {
                "summary": arch_doc.summary if arch_doc else "",
                "architecture": arch_doc.architecture if arch_doc else "",
                "files_to_modify": json.loads(arch_doc.files_to_modify) if arch_doc else ["index.html"],
                "files_to_create": json.loads(arch_doc.files_to_create) if arch_doc else [],
                "dependencies": json.loads(arch_doc.dependencies) if arch_doc and arch_doc.dependencies else [],
                "implementation_steps": json.loads(arch_doc.implementation_steps) if arch_doc else []
            }
        finally:
            db.close()

        if self._is_cancelled(task_id):
            return

        # Step 3: Development
        self._update_task_state(task_id, TaskState.DEVELOPMENT, current_agent=AgentName.DEVELOPER.value)
        await manager.broadcast(task_id, "orchestrator", "working", "Architecture Approved! Developer Agent implementing changes...")

        try:
            dev_result = await developer_agent.execute(
                task_id=task_id,
                prd_data=prd_data,
                arch_data=arch_data,
                branch_name=branch_name
            )
        except Exception as e:
            self._update_task_state(task_id, TaskState.DEVELOPMENT_FAILED, error=str(e))
            await manager.broadcast(task_id, "orchestrator", "failed", f"Developer Agent failed: {str(e)}")
            return

        # Step 4: Testing & Autonomous Self-Correction Loop
        self._update_task_state(task_id, TaskState.TESTING, current_agent=AgentName.TESTER.value)
        await manager.broadcast(task_id, "orchestrator", "working", "Developer finished. Tester Agent running Playwright browser suite...")

        try:
            test_result = await tester_agent.execute(task_id, prd_data, is_retest=False)
        except Exception as e:
            logger.error(f"Tester Agent execution failed for task {task_id}: {str(e)}", exc_info=True)
            self._update_task_state(task_id, TaskState.TEST_FAILED, current_agent=AgentName.TESTER.value, error=str(e))
            db = SessionLocal()
            try:
                run = db.query(AgentRun).filter(AgentRun.task_id == task_id, AgentRun.agent_name == AgentName.TESTER.value).order_by(AgentRun.started_at.desc()).first()
                if run and run.status == "started":
                    run.status = "failed"
                    run.error = str(e)
                    run.completed_at = datetime.now(timezone.utc)
                    db.commit()
            finally:
                db.close()
            await manager.broadcast(task_id, "orchestrator", "failed", f"Tester Agent failed to execute: {str(e)}")
            return

        retries = 0
        while test_result.get("status") == "failed" and retries < self.max_retries:
            retries += 1
            # Update retry count in DB
            db = SessionLocal()
            try:
                t = db.query(Task).filter(Task.id == task_id).first()
                if t:
                    t.retry_count = retries
                    db.commit()
            finally:
                db.close()

            # SELF-CORRECTION STEP 1: Debug Agent
            self._update_task_state(task_id, TaskState.DEBUGGING, current_agent=AgentName.DEBUG.value)
            await manager.broadcast(
                task_id,
                "orchestrator",
                "working",
                f"Test failure detected! Debug Agent investigating root cause (Attempt {retries}/{self.max_retries})..."
            )

            debug_report = await debug_agent.execute(
                task_id=task_id,
                test_results=test_result,
                prd_data=prd_data,
                arch_data=arch_data
            )

            # SELF-CORRECTION STEP 2: Developer Agent fixes the issue
            self._update_task_state(task_id, TaskState.FIXING, current_agent=AgentName.DEVELOPER.value)
            await manager.broadcast(task_id, "orchestrator", "working", "Developer Agent applying fix based on Debug diagnosis...")

            await developer_agent.execute(
                task_id=task_id,
                prd_data=prd_data,
                arch_data=arch_data,
                branch_name=branch_name,
                fix_plan=debug_report
            )

            # SELF-CORRECTION STEP 3: Tester runs again
            self._update_task_state(task_id, TaskState.RETESTING, current_agent=AgentName.TESTER.value)
            await manager.broadcast(task_id, "orchestrator", "working", "Retesting application with Playwright browser suite...")

            try:
                test_result = await tester_agent.execute(task_id, prd_data, is_retest=True)
            except Exception as e:
                logger.error(f"Tester Agent retest failed for task {task_id}: {str(e)}", exc_info=True)
                self._update_task_state(task_id, TaskState.TEST_FAILED, current_agent=AgentName.TESTER.value, error=str(e))
                db = SessionLocal()
                try:
                    run = db.query(AgentRun).filter(AgentRun.task_id == task_id, AgentRun.agent_name == AgentName.TESTER.value).order_by(AgentRun.started_at.desc()).first()
                    if run and run.status == "started":
                        run.status = "failed"
                        run.error = str(e)
                        run.completed_at = datetime.now(timezone.utc)
                        db.commit()
                finally:
                    db.close()
                await manager.broadcast(task_id, "orchestrator", "failed", f"Tester Agent failed during retest: {str(e)}")
                return

        if test_result.get("status") == "failed":
            self._update_task_state(task_id, TaskState.NEEDS_HUMAN_REVIEW, error="Max retry attempts reached without passing tests.")
            await manager.broadcast(
                task_id,
                "orchestrator",
                "needs_human_review",
                f"Automated fixing reached limit ({self.max_retries} attempts). Status: NEEDS_HUMAN_REVIEW."
            )
            return

        if self._is_cancelled(task_id):
            return

        # Step 5: Reviewer Agent
        self._update_task_state(task_id, TaskState.REVIEW, current_agent=AgentName.REVIEWER.value)
        await manager.broadcast(task_id, "orchestrator", "working", "Tests passed! Reviewer Agent conducting final code & security audit...")

        review_result = await reviewer_agent.execute(
            task_id=task_id,
            prd_data=prd_data,
            arch_data=arch_data,
            test_results=test_result
        )

        if review_result.get("status") != "approved":
            self._update_task_state(task_id, TaskState.REVIEW_FAILED, error=review_result.get("summary"))
            await manager.broadcast(task_id, "orchestrator", "failed", "Reviewer rejected changes.")
            return

        if self._is_cancelled(task_id):
            return

        # Step 6: Create GitHub Pull Request
        self._update_task_state(task_id, TaskState.PR_CREATING, current_agent=None)
        await manager.broadcast(task_id, "orchestrator", "working", "Review approved! Creating GitHub Pull Request...")

        # Build comprehensive PR markdown body
        reqs_md = "\n".join([f"- {r}" for r in prd_data.get("requirements", [])])
        test_summary_md = f"Status: **{test_result.get('status', 'passed').upper()}**\n\n"
        for r in test_result.get("requirements", []):
            icon = "✅" if r["status"] == "passed" else "❌"
            test_summary_md += f"{icon} **{r['requirement']}**: {r.get('evidence', '')}\n"

        screenshots_md = "\n".join([f"- Screenshot: `{s}`" for s in test_result.get("screenshots", [])])

        pr_title = f"feat: {prd_data.get('title', feature_request[:60])}"
        pr_body = f"""# Nexus Generated Pull Request

## Feature
{feature_request}

## Requirements
{reqs_md}

## Implementation
{dev_result.get('summary', 'Autonomous implementation completed')}

## Test Results
{test_summary_md}

## Screenshots
{screenshots_md}

## Review
{review_result.get('summary', 'Approved by Nexus Reviewer Agent')}
"""

        parsed_repo = parse_github_repo(repo_url)
        github_token = settings.GITHUB_TOKEN.strip() if settings.GITHUB_TOKEN else ""

        # Real GitHub remote push if configured
        if parsed_repo and github_token:
            owner, repo_name = parsed_repo
            auth_remote_url = f"https://x-access-token:{github_token}@github.com/{owner}/{repo_name}.git"
            await manager.broadcast(
                task_id,
                "orchestrator",
                "working",
                f"Pushing branch '{branch_name}' to remote repository '{owner}/{repo_name}'..."
            )
            setup_remote(task_id, auth_remote_url, remote_name="origin")
            push_res = git_push(task_id, branch_name=branch_name, remote="origin")
            if not push_res.get("success"):
                err_msg = push_res.get("stderr") or push_res.get("stdout") or "Push failed"
                logger.error(f"Failed to push task branch to GitHub for task {task_id}: {err_msg}")
                self._update_task_state(task_id, TaskState.NEEDS_HUMAN_REVIEW, error=f"Git push failed: {err_msg}")
                await manager.broadcast(
                    task_id,
                    "orchestrator",
                    "failed",
                    f"Failed to push branch to GitHub remote: {err_msg}"
                )
                return

        pr_info = create_pull_request(
            repo_url=repo_url,
            branch_name=branch_name,
            title=pr_title,
            body=pr_body
        )

        if not pr_info.get("success", True):
            err_msg = pr_info.get("message", "GitHub PR creation failed")
            logger.error(f"Task {task_id}: PR creation failed: {err_msg}")
            self._update_task_state(task_id, TaskState.NEEDS_HUMAN_REVIEW, error=err_msg)
            await manager.broadcast(
                task_id,
                "orchestrator",
                "failed",
                f"Failed to create GitHub Pull Request: {err_msg}"
            )
            return

        # Save PR in database
        db = SessionLocal()
        try:
            pr_record = PullRequest(
                task_id=task_id,
                pr_number=pr_info.get("pr_number"),
                pr_url=pr_info.get("pr_url"),
                branch_name=branch_name,
                title=pr_title,
                body=pr_body,
                status="open"
            )
            db.add(pr_record)

            t = db.query(Task).filter(Task.id == task_id).first()
            if t:
                t.github_pr_url = pr_info.get("pr_url")
                t.status = TaskState.COMPLETED.value
            db.commit()
        finally:
            db.close()

        self._update_task_state(task_id, TaskState.COMPLETED)
        await manager.broadcast(
            task_id,
            "orchestrator",
            "completed",
            f"Task fully completed! Pull Request created: {pr_info.get('pr_url')}",
            data={"pull_request": pr_info}
        )

    async def reject_architecture(self, task_id: str, feedback: str):
        self._update_task_state(task_id, TaskState.ARCHITECTURE_FAILED, error=feedback)
        await manager.broadcast(task_id, "orchestrator", "rejected", f"Architecture rejected by user: {feedback}")

    async def cancel_task(self, task_id: str):
        self._update_task_state(task_id, TaskState.CANCELLED)
        await manager.broadcast(task_id, "orchestrator", "cancelled", "Task execution cancelled by user.")

orchestrator = NexusOrchestrator()
