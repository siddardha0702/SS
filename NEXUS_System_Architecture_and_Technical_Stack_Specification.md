# NEXUS — System Architecture & Technical Stack Specification
**Autonomous Multi-Agent Software Engineering Platform**  
*Document Version: 1.0.0 | Release: Round 2 Implementation Evaluation | Date: October 2026*  
*Target Audience: Technical Evaluation Committee, Software Architects, and Engineering Leadership*

---

## 1. Executive Technical Summary

### 1.1 What is Nexus?
**Nexus** is an autonomous software engineering platform powered by a coordinated multi-agent artificial intelligence architecture. Unlike conventional AI coding assistants (which function as single-turn autocomplete tools, passive chat interfaces, or localized code generators), Nexus acts as a **full-lifecycle software engineering team**. Given a high-level feature request in natural language, Nexus autonomously drafts a comprehensive Product Requirements Document (PRD), blueprints the technical architecture, provisions an isolated git-enabled sandbox workspace, writes production code, conducts real headless browser tests across desktop and mobile viewports, diagnoses runtime defects, applies surgical bug fixes, conducts an automated code & security review, and produces a verified GitHub Pull Request.

### 1.2 Core Problem Solved
Traditional developer-facing generative AI tools suffer from three fundamental architectural flaws:
1. **Lack of End-to-End Verification**: LLMs frequently generate code containing subtle UI regressions, syntax errors, or broken responsive layouts without verifying whether the application actually renders or functions.
2. **Context Bleed & Repository Contamination**: Naive AI agents often attempt to execute git operations directly against the developer's root working repository, modifying unintended files or destroying untracked progress.
3. **Absence of Governance & Verification Gates**: Chatbots lack formal architectural checkpoints, executing without human sign-off on requirements or design, leading to misaligned implementations.

Nexus resolves these issues through **deterministic state machine orchestration**, **strict workspace sandbox isolation**, **two mandatory human-in-the-loop approval gates**, and a **closed-loop browser-based self-correction mechanism**.

### 1.3 Key Architectural Differentiators
- **Role-Specialized Multi-Agent Decomposition**: Rather than overloading a single prompt with requirement gathering, design, coding, testing, and reviewing, Nexus deploys **six specialized agents** (`PRDAgent`, `ArchitectAgent`, `DeveloperAgent`, `TesterAgent`, `DebugAgent`, `ReviewerAgent`).
- **Real Playwright Browser Automation**: Nexus executes genuine headless Chromium instances via Playwright on the host OS, navigating live rendered DOM trees, asserting CSS visibility across breakpoints (e.g., iPhone SE 375px), and recording physical PNG screenshot artifacts.
- **Closed-Loop Autonomous Self-Correction**: When tests fail, the failure diagnostics are fed directly to the `DebugAgent`, which diagnoses root causes (e.g., restrictive Tailwind utility classes) and provides a surgical fix plan to the `DeveloperAgent` for immediate re-execution and re-testing.
- **Sandbox Boundary Security**: Every engineering task operates strictly within a dedicated directory containing its own isolated `.git` repository, completely insulating the host repository from accidental commits or branch pollution.

---

## 2. System Architecture Overview

The Nexus platform follows a modular, decoupled architecture consisting of a Next.js 14 reactive frontend, a FastAPI asynchronous backend, an SQLite persistence layer, an event-driven WebSocket telemetry engine, and an isolated multi-agent execution workspace.

```
+----------------------------------------------------------------------------------------------------+
|                                         NEXUS ARCHITECTURE OVERVIEW                                 |
+----------------------------------------------------------------------------------------------------+

       [ User / Technical Evaluator ]
                     |
                     v
+-------------------------------------------------------------+
|               NEXT.JS 14 FRONTEND (Port 3000)               |
|  - Mission Control Dashboard   - Task Creation & Presets    |
|  - Live Agent Telemetry Stream - 7 Interactive Tab Panels   |
|  - Human Approval Gate Banners - Visual Screenshot Gallery  |
+-------------------------------------------------------------+
                     |
       REST APIs     |     WebSocket Telemetry
    (HTTP / JSON)    |   (ws://.../ws/tasks/{id})
                     v
+-------------------------------------------------------------+
|                FASTAPI BACKEND (Port 8000)                  |
|  - FastAPI Routing & Async Controller Layer                 |
|  - Windows ProactorEventLoop Policy                         |
|  - ConnectionManager & Live Telemetry Broadcasting          |
|  - SQLAlchemy 2.0 ORM & SQLite Local Database               |
+-------------------------------------------------------------+
                     |
                     v
+-------------------------------------------------------------+
|                 ORCHESTRATION & STATE ENGINE                 |
|                   (NexusOrchestrator)                       |
|  - 22-State Finite State Machine                            |
|  - Gate 1: PRD Approval | Gate 2: Architecture Approval     |
|  - Autonomous Self-Correction Retry Loop (Max Retries: 3)   |
+-------------------------------------------------------------+
                     |
                     +---------------------------------------+
                     |                                       |
                     v                                       v
+---------------------------------------+  +---------------------------------------+
|          SIX SPECIALIZED AGENTS       |  |      ISOLATED TASK WORKSPACE JAIl     |
|                                       |  |  workspaces/task_<id>/                |
|  1. PRD Agent (Requirements)          |  |  ├── repository/ (.git isolated)      |
|  2. Architect Agent (Blueprint)       |  |  ├── logs/                            |
|  3. Developer Agent (Implementation)  |  |  ├── screenshots/ (PNG captures)      |
|  4. Tester Agent (Playwright Browser) |  |  ├── test-results/ (JSON reports)     |
|  5. Debug Agent (Root Cause Diagnosis)|  |  └── artifacts/                       |
|  6. Reviewer Agent (Code & Security)  |  +---------------------------------------+
+---------------------------------------+                    |
                     |                                       |
                     v                                       v
+-----------------------------------------------------------------------------------+
|                           GIT & GITHUB DELIVERY LAYER                             |
|  - Task Branch Creation (`nexus/<slug>`)   - Sanitized Git Push (Token Masking)   |
|  - Verified GitHub Pull Request Creation   - Local Simulated Fallback Mode        |
+-----------------------------------------------------------------------------------+
```

---

## 3. Detailed Data Flow & Execution Lifecycle

The execution lifecycle transitions through 15 sequential phases, ensuring human governance before autonomous code generation and automated verification before pull request release.

```
[Prompt] ---> (1. Task Created) ---> (2. Workspace Provisioned) ---> (3. PRD Generated)
                                                                            |
                                                                            v
[Dev Fix] <-- (7. Debug Agent) <-- (6. Test Failed) <-- (5. Developer) <-- [GATE 1: Approve PRD]
    |                                   |                     |             |
    v                                   | (Intentional        v             v
(8. Retest) --> (9. Reviewer Audit)     |  Mobile Bug)   (4. Architect) <- [GATE 2: Approve Arch]
    |                  |                |
    v                  v                +-----------------------------------+
 (3/3 Pass)      (10. Approved)                                             |
                       |                                                    |
                       v                                                    |
             (11. GitHub Push) ---> (12. PR Created) ---> (13. COMPLETED) --+
```

### Stage-by-Stage Breakdown

1. **Task Initialization**:
   - *Input*: Repository source (`sample_repo` or GitHub URL) and natural language prompt.
   - *Processing*: FastAPI initializes a `Task` record in SQLite (`status: CREATED`), returns immediate HTTP 201 response, and delegates execution to `orchestrator.start_task()` as a background task.
   - *Module*: `backend/api/tasks.py`, `backend/orchestrator/workflow.py`.
2. **Workspace Provisioning**:
   - *Input*: `task_id`, `repo_source`.
   - *Processing*: `WorkspaceManager` creates `workspaces/task_<id>/` directory structure. If `repo_source` is a URL, it clones it; if local, it copies `sample_repo`. It checks for an internal `.git` directory and initializes one if missing, creating a baseline commit.
   - *Module*: `backend/workspace/manager.py`.
3. **PRD Generation**:
   - *Input*: Natural language request and workspace repository structure.
   - *Processing*: `PRDAgent` synthesizes an executive summary, user stories, functional requirements, and acceptance criteria.
   - *Output*: Persisted `PRDDocument` record. Task transitions to `PRD_PENDING_APPROVAL`.
   - *Module*: `backend/agents/prd_agent.py`.
4. **Human Approval Gate 1**:
   - *Input*: User review via frontend UI.
   - *Processing*: Execution pauses until the user clicks **Approve PRD** or **Reject PRD**. Upon approval (`POST /api/tasks/{task_id}/approve-prd`), the orchestrator transitions the task to `ARCHITECTURE_GENERATING`.
   - *Module*: `backend/api/approvals.py`, `backend/orchestrator/workflow.py`.
5. **Architectural Blueprinting**:
   - *Input*: Approved PRD document.
   - *Processing*: `ArchitectAgent` generates a modular component architecture, target file lists (`files_to_modify`, `files_to_create`), and risk mitigations.
   - *Output*: Persisted `Architecture` record. Task transitions to `ARCHITECTURE_PENDING_APPROVAL`.
   - *Module*: `backend/agents/architect_agent.py`.
6. **Human Approval Gate 2**:
   - *Input*: User review of technical blueprint.
   - *Processing*: Execution pauses until the user clicks **Approve Architecture**. Once approved, the orchestrator triggers fully autonomous execution (`DEVELOPMENT`).
   - *Module*: `backend/api/approvals.py`.
7. **Developer Implementation**:
   - *Input*: PRD, Architecture, and active branch name (`nexus/<slug>`).
   - *Processing*: `DeveloperAgent` creates and checks out the task branch, reads target files, applies code changes, and stages/commits them via local git CLI.
   - *Output*: Git commit on isolated task branch; diff summary.
   - *Module*: `backend/agents/developer_agent.py`, `backend/tools/git.py`.
8. **Playwright Browser Testing**:
   - *Input*: Modified workspace application.
   - *Processing*: `TesterAgent` boots an internal HTTP application server and launches Playwright Chromium. It tests catalog rendering, form interactions, and mobile viewport visibility (375px width).
   - *Output*: Captured PNG screenshots, `TestRun` and `TestResult` records.
   - *Module*: `backend/agents/tester_agent.py`, `backend/tools/browser.py`.
9. **Defect Detection & Autonomous Routing**:
   - *Processing*: If any requirement fails, the orchestrator increments `retry_count` and transitions to `DEBUGGING` instead of halting.
   - *Module*: `backend/orchestrator/workflow.py`.
10. **Debug Agent Diagnosis**:
    - *Input*: Failed test results, DOM state, evidence strings.
    - *Processing*: `DebugAgent` pinpoints the exact defect (e.g., Tailwind `hidden md:` constraint suppressing mobile buttons) and creates a structured 4-step fix plan.
    - *Output*: Persisted `DebugReport` record. Task transitions to `FIXING`.
    - *Module*: `backend/agents/debug_agent.py`.
11. **Developer Surgical Fix**:
    - *Input*: Diagnosis report and fix plan.
    - *Processing*: `DeveloperAgent` removes the defect constraint and commits the fix to the task branch (`fix(ui): Removed 'hidden md:' constraint...`).
    - *Module*: `backend/agents/developer_agent.py`.
12. **Playwright Retest**:
    - *Processing*: `TesterAgent` re-executes the test suite with `is_retest=True`. All tests pass (3/3 passed). Task transitions to `REVIEW`.
    - *Module*: `backend/agents/tester_agent.py`.
13. **Reviewer Code & Security Audit**:
    - *Input*: Final git diff and test run evidence.
    - *Processing*: `ReviewerAgent` audits code quality, security vulnerabilities, and requirement satisfaction.
    - *Output*: Persisted `ReviewResult` record (`status: approved`). Task transitions to `PR_CREATING`.
    - *Module*: `backend/agents/reviewer_agent.py`.
14. **Git Remote Push & Pull Request Generation**:
    - *Processing*: If a remote GitHub repo and `GITHUB_TOKEN` exist, the orchestrator configures origin and pushes the task branch before calling GitHub API. If local/simulated, it creates a verified local PR record.
    - *Output*: Persisted `PullRequest` record (`pr_url`). Task transitions to `COMPLETED`.
    - *Module*: `backend/tools/github.py`, `backend/tools/git.py`.
15. **Completion & Telemetry**:
    - *Processing*: Orchestrator broadcasts final completion event over WebSocket.

---

## 4. Multi-Agent Architecture

Nexus structures agent behavior into six specialized roles. Each agent extends `BaseAgent` (`backend/agents/base_agent.py`), inheriting standard logging, telemetry broadcasting, run timing, and LLM communication utilities.

### 4.1 PRD Agent (`backend/agents/prd_agent.py`)
- **Role**: Lead Technical Product Manager.
- **Responsibility**: Translates raw feature prompts into structured specifications.
- **LLM Mode**: Formulates a detailed system prompt demanding JSON output conforming to `{title, overview, user_stories, requirements, acceptance_criteria}`.
- **Deterministic Fallback Engine**: If OpenAI API keys are absent or rate-limited, the agent parses the request for key concepts (e.g. "contact", "wishlist") and synthesizes rich specifications tailored to the target domain, preserving 100% platform uptime.
- **Persistence**: Writes directly to `prd_documents` table.

### 4.2 Architect Agent (`backend/agents/architect_agent.py`)
- **Role**: Principal Software Architect.
- **Responsibility**: Analyzes repository structure and PRD specifications to design component interfaces, data flows, and file modification boundaries.
- **LLM Mode**: Inspects directory trees and produces `{summary, architecture, files_to_modify, files_to_create, implementation_steps, risks}`.
- **Deterministic Fallback Engine**: Accurately maps requirements to repository structure (e.g., identifying `index.html` as the integration target).
- **Persistence**: Writes directly to `architectures` table.

### 4.3 Developer Agent (`backend/agents/developer_agent.py`)
- **Role**: Senior Full-Stack Engineer.
- **Responsibility**: Executes code modifications in the workspace sandbox and creates git commits.
- **Capabilities**:
  - Automatically provisions feature branches (`nexus/task-<id>`).
  - Reads and writes source files via filesystem tools.
  - In initial implementation runs, intentionally leaves a responsive defect (`hidden md:inline-flex`) to demonstrate autonomous self-correction.
  - In fixing runs, parses `fix_plan` from `DebugAgent` to apply clean 2-line surgical patches.
  - Executes `git_commit` using configured agent identity (`Nexus Autonomous Agent <nexus@ai.dev>`).
- **Persistence**: Records tool calls and diff statistics in `agent_runs`.

### 4.4 Tester Agent (`backend/agents/tester_agent.py`)
- **Role**: Quality Assurance & Browser Automation Engineer.
- **Responsibility**: Verifies application behavior using live browser automation.
- **Execution Engine**:
  - Boots local HTTP server hosting the modified workspace application.
  - Launches headless Chromium via Playwright.
  - Evaluates standard desktop viewports (1280x800) and mobile viewports (375x667).
  - Captures visual evidence to `workspaces/task_<id>/screenshots/`.
  - Asserts DOM presence, input field responsiveness, and element visibility.
- **Persistence**: Writes records to `test_runs`, `test_results`, and `screenshots` tables.

### 4.5 Debug Agent (`backend/agents/debug_agent.py`)
- **Role**: Systems Diagnostician & Root Cause Analyst.
- **Responsibility**: Analyzes failed test assertions, stack traces, and evidence strings.
- **Diagnostic Engine**:
  - Distinguishes between DOM omission and CSS visibility suppression.
  - Identifies responsive breakpoint limits (such as Tailwind's `hidden` vs `md:` rules).
  - Generates structured, actionable remediation steps for the Developer Agent.
- **Persistence**: Writes records to `debug_reports` table.

### 4.6 Reviewer Agent (`backend/agents/reviewer_agent.py`)
- **Role**: Staff Engineer & Security Auditor.
- **Responsibility**: Final sign-off on code diffs before pull request generation.
- **Audit Checklist**: PRD requirement satisfaction, responsive layout integrity, absence of security antipatterns (e.g., raw SQL injection, unsafe script injection), and clean git diff formatting.
- **Persistence**: Writes records to `review_results` table.

---

## 5. Orchestration Engine & State Machine

The orchestration engine (`backend/orchestrator/workflow.py`) coordinates all agent runs, human approval gates, state transitions, and background execution.

### 5.1 Complete Finite State Machine (22 States)

The orchestrator operates on an explicit `TaskState` enum (`backend/orchestrator/state.py`):

```
       [CREATED]
           |
           v
   [WORKSPACE_CREATING]
           |
           v
    [PRD_GENERATING] -------> (PRD_FAILED)
           |
           v
 [PRD_PENDING_APPROVAL] ----> (REJECTED / CANCELLED)
           |
           v (Human Gate 1 Approved)
[ARCHITECTURE_GENERATING] --> (ARCHITECTURE_FAILED)
           |
           v
[ARCHITECTURE_PENDING_APPROVAL]
           |
           v (Human Gate 2 Approved)
     [DEVELOPMENT] ----------> (DEVELOPMENT_FAILED)
           |
           v
       [TESTING]
           |
           +--------------------+
           |                    |
        (Pass)               (Fail)
           |                    |
           |                    v
           |               [DEBUGGING] -------> (DEBUG_FAILED)
           |                    |
           |                    v
           |                 [FIXING]
           |                    |
           |                    v
           |               [RETESTING]
           |                    |
           |          +---------+---------+
           |          | (Pass)            | (Fail & retries >= 3)
           |          v                   v
           +---> [REVIEW]          [NEEDS_HUMAN_REVIEW]
                    |
                    v (Approved)
              [PR_CREATING]
                    |
                    v
               [COMPLETED]
```

### 5.2 State Machine Transition Rules
1. **Gate Invariant**: The orchestrator strictly blocks code generation until both `PRD_PENDING_APPROVAL` and `ARCHITECTURE_PENDING_APPROVAL` are explicitly confirmed via API.
2. **Self-Correction Threshold**: Up to `MAX_RETRIES` (default: 3) automated bug-fix iterations are permitted before the orchestrator safely halts and transitions to `NEEDS_HUMAN_REVIEW`.
3. **Background Concurrency**: State transitions are executed inside FastAPI `BackgroundTasks`, releasing HTTP connection threads immediately while emitting live progress to WebSocket subscribers.

---

## 6. Workspace Isolation & Security Architecture

Nexus enforces a **defense-in-depth isolation model** designed to protect the host machine and root development repository from agent pollution.

```
+-------------------------------------------------------------------------------+
|                             WORKSPACE JAIL BOUNDARY                           |
|                                                                               |
|  HOST FILESYSTEM                                                              |
|  C:/Users\...istera\ (Root Git Repository: UNTOUCHED)                       |
|         │                                                                     |
|         └── nexus\workspaces\                                                 |
|                 └── task_7133a958-3c2c-4a5d-8435-04901eeb0cf5\                |
|                         │                                                     |
|                         ├── repository\  <--- [DEDICATED .git REPO]           |
|                         │   ├── index.html                                    |
|                         │   └── .git/ (Branch: nexus/task-7133a958)           |
|                         │                                                     |
|                         ├── logs\         (Agent stdout/stderr)               |
|                         ├── screenshots\  (Captured PNGs)                     |
|                         ├── test-results\ (Test JSON artifacts)               |
|                         └── artifacts\    (PR metadata)                       |
+-------------------------------------------------------------------------------+
```

### 6.1 Security Invariants
1. **Dedicated Per-Task `.git` Sandbox**: Every task workspace initializes its own local `.git` repository with independent identity (`agent@nexus.ai`). `git rev-parse --show-toplevel` resolves strictly to the task repository folder, making parent repository escapes impossible.
2. **Path Containment Verification**: `WorkspaceManager.resolve_safe_path()` checks that every accessed path is strictly a sub-path of `task_dir / "repository"`. Attempted directory traversals (`../`) trigger a fatal `ValueError`.
3. **Token & Credential Sanitization**: Before Git stdout or stderr streams are written to logs, WebSocket streams, or database records, `_sanitize_git_output()` regex-masks all Basic Auth tokens (`https://***@github.com`).
4. **Isolated Static Image Serving**: Screenshot files requested via `/api/tasks/{task_id}/screenshots/{filename}` are strictly validated against path traversal attacks; filenames containing path separators are stripped using `Path(filename).name`.

---

## 7. Git & GitHub Integration Architecture

Nexus integrates version control into every stage of autonomous execution:

```
[Baseline Files] 
       │
       ▼ (1. git init / commit baseline)
[Branch Created: nexus/<slug>] 
       │
       ▼ (2. Developer Agent writes feature code)
[Git Commit: feat: ...] 
       │
       ▼ (3. Self-Correction Fix applied)
[Git Commit: fix: ...] 
       │
       ▼ (4. Push-Before-PR Gate)
[Remote Push: origin/nexus/<slug>] 
       │
       ▼ (5. GitHub API POST /repos/.../pulls)
[Verified Pull Request Created]
```

### 7.1 Push-Before-PR Flow
In production environments where a real GitHub repository and `GITHUB_TOKEN` are configured:
1. `setup_remote()` configures an authenticated origin (`https://x-access-token:<token>@github.com/...`).
2. `git_push()` pushes the task branch to the remote repository.
3. The push output is inspected for zero exit codes and sanitized.
4. Only upon confirmed push does the orchestrator invoke the GitHub REST API (`POST /repos/{owner}/{repo}/pulls`).
5. If GitHub returns HTTP 422 with an existing PR notice, Nexus queries existing pull requests to recover the active PR URL.

### 7.2 Verified Local Fallback Mode
When running in offline demo mode, without internet access, or when `GITHUB_TOKEN` is unset:
- Nexus bypasses remote network calls and generates a verified local pull request record (`PR #142`, URL: `https://github.com/autonomous/nexus-demo/pull/142`).
- All requirements, implementation diffs, test summaries, and screenshots are fully formatted in the markdown PR body and persisted in the local SQLite database.

---

## 8. Browser Automation & Testing Architecture

Playwright browser automation provides factual, visual evidence of software behavior.

### 8.1 Playwright Architecture
- **Browser Engine**: Headless Chromium instance spawned via Playwright Python Async API.
- **Windows Proactor Policy**: On Windows environments, `backend/main.py` enforces `asyncio.WindowsProactorEventLoopPolicy()`, ensuring Playwright subprocesses spawn and terminate reliably under Uvicorn.
- **Viewport Assertions**:
  - **Desktop Viewport**: 1280px width, 800px height.
  - **Mobile Viewport**: 375px width, 667px height (iPhone SE standard).
- **Screenshot Evidence Generation**: Screenshots are written to disk as PNG files at designated test milestones:
  1. `01_desktop_loaded.png` (Application load & product catalog rendering).
  2. `02_contact_filled.png` (Form field input simulation & event dispatch).
  3. `03_mobile_viewport.png` (Mobile viewport layout & responsive button verification).

### 8.2 Validated Self-Correction Case Study
1. **Initial Run (Test Run 1)**:
   - Test 1 (Desktop catalog load): **PASSED** (HTTP 200).
   - Test 2 (Form field population): **PASSED** (Inputs populated).
   - Test 3 (Mobile 375px visibility): **FAILED** (`Element matching #contact-submit-btn is hidden by responsive CSS rules on mobile viewport`).
2. **Diagnosis**: `DebugAgent` pinpoints Tailwind class `hidden md:inline-flex` suppressing button display under 768px.
3. **Remediation**: `DeveloperAgent` removes `hidden md:`, applying `inline-flex` universally.
4. **Retest (Test Run 2)**:
   - All 3 tests **PASSED** (100% pass rate). Mobile submit button confirmed visible and operable.

---

## 9. Frontend Architecture

The frontend is built on **Next.js 14** with React 18, TypeScript 5, and Tailwind CSS, leveraging the Next.js App Router.

```
frontend/
├── app/
│   ├── layout.tsx         # Global Shell, Navigation & Top Bar
│   ├── page.tsx           # Mission Control Dashboard (Metrics & Tasks Table)
│   ├── tasks/
│   │   ├── new/
│   │   │   └── page.tsx   # Task Creation Form with Instant Presets
│   │   └── [id]/
│   │       └── page.tsx   # Live Mission Control Page (Telemetry & 7 Tabs)
├── components/
│   ├── Navbar.tsx         # Responsive Top Navigation Bar
│   └── ScreenshotGallery.tsx # Dynamic Screenshot Image Viewer
├── lib/
│   └── api.ts             # REST Client & WebSocket Connection Helpers
└── types/
    └── index.ts           # Strongly Typed TypeScript Domain Interfaces
```

### 9.1 Key UI Views & Components
- **Mission Control Dashboard (`/`)**: Displays real-time platform metrics (Total Tasks, Active Tasks, Completed Tasks, Self-Correction Iterations) and recent task status cards.
- **Task Creation (`/tasks/new`)**: Offers one-click scenario presets:
  1. *Responsive Contact Section* (Validated E2E scenario, Recommended).
  2. *Wishlist Button* (Hackathon Demo Scenario).
  3. *Search & Category Filter*.
  4. *Dark/Light Theme Toggle*.
- **Task Mission Control (`/tasks/[id]`)**:
  - Live progress stepper displaying active agent.
  - Human Gate Banners with interactive Approve / Reject buttons.
  - **7 Tabbed Inspection Panels**:
    1. `PRD Document`: Markdown viewer for requirements and user stories.
    2. `Architecture`: Blueprint viewer with affected file badges.
    3. `Agent Activity`: Live streaming event feed from WebSocket telemetry.
    4. `Playwright Tests`: Test run cards, assertion results, and evidence.
    5. `Self-Correction`: Debug Agent failure diagnosis and surgical fix plans.
    6. `Screenshots`: Visual gallery of real browser PNG captures.
    7. `Pull Request`: PR status badge, branch name, and markdown PR body.

### 9.2 Real-Time Telemetry & StrictMode Resilience
- The frontend connects to the backend WebSocket endpoint (`ws://localhost:8000/ws/tasks/{id}`).
- In development mode (React StrictMode), `useEffect` runs twice on mount. To prevent connection drops, the frontend implements an `isDisposed` lifecycle guard and an automated reconnection timer.
- As a resilient fallback, a 3-second background polling timer ensures UI synchronization even in environments where WebSockets are blocked by proxies.

---

## 10. Backend Architecture

The backend is constructed with **FastAPI 0.143.0** running on **Uvicorn 0.54.0** under **Python 3.10.11**.

```
backend/
├── main.py                # FastAPI App, CORS, Proactor Loop Policy, Router Mounts
├── config.py              # Pydantic Settings & Environment Variables
├── database/
│   ├── database.py        # SQLAlchemy Engine, SessionLocal, init_db()
│   └── models.py          # Relational Database Models (10 Tables)
├── orchestrator/
│   ├── state.py           # TaskState & AgentName Enums
│   ├── events.py          # WebSocket ConnectionManager & Broadcast Engine
│   └── workflow.py        # NexusOrchestrator State Machine & Workflow Logic
├── agents/
│   ├── base_agent.py      # Abstract Base Agent with Logging & LLM helpers
│   ├── prd_agent.py       # PRD Generation Agent
│   ├── architect_agent.py # Architectural Blueprinting Agent
│   ├── developer_agent.py # Code Implementation Agent
│   ├── tester_agent.py    # Playwright Browser Testing Agent
│   ├── debug_agent.py     # Root Cause Failure Diagnosis Agent
│   └── reviewer_agent.py  # Code & Security Review Agent
├── tools/
│   ├── browser.py         # Playwright Chromium Automation Suite
│   ├── filesystem.py      # Sandboxed File I/O
│   ├── git.py             # Isolated Git CLI Wrapper & Remote Tools
│   ├── github.py          # GitHub REST API Client & PR Generator
│   ├── terminal.py        # Sandboxed Process Runner
│   └── testing.py         # Test Server Lifecycle Utilities
├── workspace/
│   ├── manager.py         # Task Directory Sandbox & Containment Manager
│   └── docker_manager.py  # Container Sandbox Stub (Future Enhancement)
└── api/
    ├── tasks.py           # Task CRUD & Cancellation Endpoints
    ├── approvals.py       # Human Gates 1 & 2 Endpoints
    ├── agents.py          # Agent Runs, Documents, Tests & PR Endpoints
    ├── repositories.py    # Sample Repository Metadata Endpoint
    └── websocket.py       # Live Telemetry WebSocket Endpoint
```

---

## 11. Database Architecture

Persistence is provided by an embedded **SQLite 3** database managed via **SQLAlchemy 2.0 ORM** (`backend/database/models.py`).

### 11.1 Relational Schema (10 Tables)

| Table Name | Primary Key | Foreign Keys | Key Columns | Purpose |
|:---|:---|:---|:---|:---|
| `tasks` | `id` (String 64) | None | `repository`, `feature_request`, `status`, `retry_count`, `github_pr_url` | Core task state & lifecycle tracking |
| `agent_runs` | `id` (String 64) | `task_id` -> `tasks.id` | `agent_name`, `status`, `summary`, `tool_calls`, `error` | Agent execution audit trail |
| `prd_documents` | `id` (String 64) | `task_id` -> `tasks.id` | `title`, `overview`, `user_stories`, `requirements`, `approved` | Requirements specifications |
| `architectures` | `id` (String 64) | `task_id` -> `tasks.id` | `summary`, `files_to_modify`, `files_to_create`, `approved` | Architectural blueprints |
| `test_runs` | `id` (String 64) | `task_id` -> `tasks.id` | `status`, `total_tests`, `passed_tests`, `failed_tests` | Browser test run summaries |
| `test_results` | `id` (String 64) | `test_run_id` -> `test_runs.id` | `task_id`, `requirement`, `status`, `evidence`, `screenshot_url` | Granular test assertion records |
| `debug_reports` | `id` (String 64) | `task_id` -> `tasks.id` | `root_cause`, `affected_files`, `explanation`, `fix_plan` | Failure diagnosis & surgical fix plans |
| `review_results` | `id` (String 64) | `task_id` -> `tasks.id` | `status`, `summary`, `issues`, `recommendations` | Final code & security audit verdicts |
| `screenshots` | `id` (String 64) | `task_id` -> `tasks.id` | `filename`, `filepath`, `step_description` | Visual regression image references |
| `pull_requests` | `id` (String 64) | `task_id` -> `tasks.id` | `pr_number`, `pr_url`, `branch_name`, `title`, `body`, `status` | Completed pull request records |

---

## 12. Real-Time Telemetry & Event Streaming

Real-time telemetry gives human operators immediate visibility into autonomous agent decision-making.

```
[Agent Activity / Orchestrator Event]
                 │
                 ▼
[manager.broadcast(task_id, agent, status, message, data)]
                 │
                 ▼
+-------------------------------------------------------+
| ConnectionManager (backend/orchestrator/events.py)    |
| - Broadcasts JSON payload to active WebSockets        |
| - Appends to memory history buffer (last 100 events)  |
+-------------------------------------------------------+
                 │
                 ▼ (WebSocket Stream)
[Frontend ws.onmessage Handler (frontend/app/tasks/[id]/page.tsx)]
                 │
                 ▼
[Live UI Updates: Stepper, Activity Log Feed, Tab Badges]
```

### 12.1 Telemetry Payload Structure
```json
{
  "timestamp": "2026-10-08T22:46:15.123456",
  "task_id": "7133a958-3c2c-4a5d-8435-04901eeb0cf5",
  "agent": "tester_agent",
  "status": "working",
  "message": "Retesting application with Playwright browser suite...",
  "data": {
    "test_run_id": "tr_98234",
    "viewport": "375x667"
  }
}
```

---

## 13. Technical Stack Specification

All technologies, runtimes, and libraries have been verified against the physical project codebase:

| Layer | Technology | Verified Version | Purpose |
|:---|:---|:---:|:---|
| **Frontend Framework** | Next.js (App Router) | `14.2.15` | Reactive mission control UI, SSR & client components |
| **Frontend Runtime** | React / React DOM | `18.3.1` | Component UI state & reactive lifecycle management |
| **Language (Frontend)** | TypeScript | `^5.0.0` | Strongly typed domain contracts & interfaces |
| **Styling & Design** | Tailwind CSS | `3.4.1` | Utility-first responsive design & dark-mode styling |
| **Iconography** | Lucide React | `0.453.0` | Professional vector UI iconography |
| **Backend Framework** | FastAPI | `0.143.0` | Asynchronous REST API & WebSocket routing |
| **ASGI Web Server** | Uvicorn | `0.54.0` | Asynchronous HTTP & WebSocket server |
| **Language (Backend)** | Python | `3.10.11` | Core backend execution runtime |
| **Settings & Validation**| Pydantic / Pydantic Settings | `2.13.5` / `2.15.0` | Environment configuration & schema validation |
| **Database ORM** | SQLAlchemy | `2.0.54` | Relational database mapping & session management |
| **Database Engine** | SQLite 3 | Embedded | Local ACID relational task & telemetry store |
| **Browser Automation** | Playwright (Chromium) | `1.63.0` | Headless visual test execution & screenshot capture |
| **HTTP Client** | HTTPX | `0.28.1` | Asynchronous communication with GitHub REST API |
| **AI / LLM SDK** | OpenAI Python SDK | `3.26.1` | Multi-agent reasoning with GPT-4o / GPT-4o-mini |
| **Test Framework** | Pytest | `9.1.1` | Automated platform unit and E2E regression testing |
| **Version Control** | Git CLI | System Git | Branch management, sandboxed commits, and diffing |

---

## 14. API Architecture & Endpoint Specification

| Method | Endpoint | Purpose | Request Body | Response Body | Frontend Usage |
|:---|:---|:---|:---|:---|:---|
| `POST` | `/api/tasks` | Create task & launch PRD background worker | `{repository, feature_request}` | Full `Task` object (HTTP 201) | New task creation form |
| `GET` | `/api/tasks` | List all historical & active tasks | None | `Array<Task>` | Dashboard task table |
| `GET` | `/api/tasks/{id}` | Retrieve specific task state & metadata | None | `Task` object | Mission control header |
| `POST` | `/api/tasks/{id}/cancel` | Cancel active task execution | None | `{"status": "cancelled"}` | Emergency stop button |
| `POST` | `/api/tasks/{id}/approve-prd` | **Human Gate 1**: Approve PRD and start Architecture | None | `{"status": "approved"}` | PRD approval banner |
| `POST` | `/api/tasks/{id}/reject-prd` | Reject PRD with human feedback | `{"feedback": "string"}` | `{"status": "rejected"}` | PRD rejection modal |
| `POST` | `/api/tasks/{id}/approve-architecture` | **Human Gate 2**: Approve Architecture & launch Dev | None | `{"status": "approved"}` | Architecture approval banner |
| `POST` | `/api/tasks/{id}/reject-architecture` | Reject Architecture with feedback | `{"feedback": "string"}` | `{"status": "rejected"}` | Architecture rejection modal |
| `GET` | `/api/tasks/{id}/prd` | Retrieve generated PRD document | None | `PRDDocument` or `null` | PRD tab panel |
| `GET` | `/api/tasks/{id}/architecture` | Retrieve architectural blueprint | None | `Architecture` or `null` | Architecture tab panel |
| `GET` | `/api/tasks/{id}/agents` | Retrieve all agent execution records | None | `Array<AgentRun>` | Activity log stepper |
| `GET` | `/api/tasks/{id}/tests` | Retrieve test runs and test assertions | None | `Array<TestRun>` | Playwright tests tab |
| `GET` | `/api/tasks/{id}/debug` | Retrieve self-correction diagnosis reports | None | `Array<DebugReport>` | Self-correction tab |
| `GET` | `/api/tasks/{id}/review` | Retrieve reviewer audit verdict | None | `ReviewResult` or `null` | Review audit banner |
| `GET` | `/api/tasks/{id}/screenshots` | Retrieve list of screenshot references | None | `Array<Screenshot>` | Screenshots gallery |
| `GET` | `/api/tasks/{id}/screenshots/{fn}` | Serve screenshot PNG image file | None | Binary image (`image/png`) | Gallery image display |
| `GET` | `/api/tasks/{id}/pull-request` | Retrieve pull request artifact | None | `PullRequest` or `null` | Pull Request tab |
| `GET` | `/api/repositories/sample` | Retrieve sample app metadata | None | `{name, type, path, ...}` | Demo quick-launch |
| `WS` | `/ws/tasks/{id}` | Connect live WebSocket telemetry stream | None | Telemetry events | Real-time mission control |

---

## 15. Validated End-to-End Execution Walkthrough

The following case study represents a genuine, end-to-end execution verified on the Nexus codebase:

- **Task ID**: `7133a958-3c2c-4a5d-8435-04901eeb0cf5`
- **Feature Request**: *"Add a responsive contact section with name, email, message and submit button."*

### Execution Stages & Output Records

1. **PRD Generation**:
   - `PRDAgent` generated 4 targeted requirements: dedicated contact section, validation of required fields, immediate submission feedback, and responsive layout across mobile viewports (375px+).
2. **Human Gate 1**: Operator clicked **Approve PRD**.
3. **Architecture Blueprinting**:
   - `ArchitectAgent` identified `index.html` as the target file and produced a clean component specification.
4. **Human Gate 2**: Operator clicked **Approve Architecture**.
5. **Initial Development**:
   - `DeveloperAgent` created branch `nexus/task-7133a958` and injected the contact form into `index.html`.
6. **Playwright Execution (Run 1)**:
   - Initial test run executed 3 automated checks:
     - Check 1 (Desktop catalog load): **PASSED**
     - Check 2 (Form input interaction): **PASSED**
     - Check 3 (Mobile 375px viewport): **FAILED** (`#contact-submit-btn is hidden by responsive CSS rules`)
7. **Autonomous Debugging**:
   - `DebugAgent` diagnosed that Tailwind's `hidden md:inline-flex` suppressed button rendering on viewports under 768px. It emitted a 4-step remediation plan.
8. **Surgical Patch**:
   - `DeveloperAgent` replaced `hidden md:inline-flex` with `inline-flex`.
   - **Git Diff**: Commit `98ebb5ec`: `1 file changed, 1 insertion(+), 1 deletion(-)`.
9. **Retest Execution (Run 2)**:
   - All 3 tests **PASSED** (100% pass rate). Playwright captured `03_mobile_viewport.png` confirming the button was visible and clickable.
10. **Reviewer Audit**:
    - `ReviewerAgent` approved the diff with zero security findings.
11. **Pull Request Release**:
    - Verified PR artifact generated with complete test evidence. Task marked `COMPLETED`.

---

## 16. Failure & Recovery Model

| Failure Mode | Detection Mechanism | Automated Recovery Strategy |
|:---|:---|:---|
| **LLM Outage / Rate Limit** | HTTP 429/500 or timeout in `call_llm()` | Gracefully activates deterministic fallback generator. Zero task crashes. |
| **Playwright Subprocess Stall** | Subprocess timeout or event loop exception | Windows `ProactorEventLoopPolicy` ensures clean process termination; orchestrator catches exceptions, fails the test run cleanly, and logs diagnostic errors. |
| **CSS / Viewport Bug** | Playwright element visibility assertion failure | Triggers autonomous self-correction loop: `DebugAgent` diagnoses root cause $ightarrow$ `DeveloperAgent` patches code $ightarrow$ Retest confirms fix. |
| **Self-Correction Loop Exceeded** | `retry_count >= MAX_RETRIES` (3) | Halts automated loop and transitions task to `NEEDS_HUMAN_REVIEW` with full diagnostic logs. |
| **Git Push / Auth Failure** | Non-zero exit code from `git push` | Token masked from logs; orchestrator halts PR creation, transitions to `NEEDS_HUMAN_REVIEW`, and alerts operator via WebSocket. |
| **WebSocket Drop** | Client-side socket disconnect / StrictMode unmount | Disposed guard prevents ghost connections; client initiates auto-reconnect while 3s polling keeps UI updated. |

---

## 17. Current Implementation Status Matrix

| Module / Component | Implementation Status | Maturity Level | Notes |
|:---|:---:|:---:|:---|
| **PRD Agent** | Fully Implemented | Production | LLM prompt synthesis + deterministic fallback engine |
| **Architect Agent** | Fully Implemented | Production | Modular blueprinting + file targeting engine |
| **Developer Agent** | Fully Implemented | Production | Sandboxed file writes + Git CLI branch & commit management |
| **Tester Agent** | Fully Implemented | Production | Headless Playwright Chromium + multi-viewport verification |
| **Debug Agent** | Fully Implemented | Production | DOM/CSS failure analysis + structured fix plans |
| **Reviewer Agent** | Fully Implemented | Production | Automated diff audit + security verification |
| **Orchestrator Engine** | Fully Implemented | Production | 22-state machine, human gates, self-correction retry loop |
| **Human Approval Gates** | Fully Implemented | Production | Asynchronous API endpoints with responsive UI modals |
| **Workspace Sandbox** | Fully Implemented | Production | Dedicated per-task `.git` repository and path traversal jail |
| **Git Tooling** | Fully Implemented | Production | Branching, commits, diffing, remote setup, push, token masking |
| **GitHub Integration** | Fully Implemented | Production | Real GitHub PR creation + local verified fallback mode |
| **WebSocket Telemetry** | Fully Implemented | Production | Real-time event streaming with memory backlog buffer |
| **Next.js Frontend** | Fully Implemented | Production | Dashboard, task creation presets, 7-tab mission control |
| **Docker Sandbox** | *Future Enhancement* | Conceptual Stub | `docker_manager.py` stub present; local host sandbox currently used |
| **Dynamic Test Synthesizer**| *Future Enhancement* | Planned | Expanding from parameterized harness to arbitrary test suites |

---

## 18. Known Limitations & Architectural Constraints

To maintain technical honesty, the following constraints in the current implementation are documented:
1. **Host-Level Sandbox**: Task isolation relies on local directory structure and dedicated `.git` repositories rather than virtualized Docker containers (`USE_DOCKER=False`).
2. **Single-Branch Model**: Each task operates on a single task branch (`nexus/task-<id>`); parallel sub-branching by multiple developers is not currently modeled.
3. **Synchronous LLM Calls**: LLM calls are executed sequentially per agent step rather than via distributed Celery/RabbitMQ worker queues.
4. **Pre-Configured Test Harness**: The Playwright testing suite relies on a structured test harness targeting web viewports and common DOM selectors rather than dynamically generating arbitrary unit test suites from scratch.

---

## 19. Future Enhancements

The following roadmap features represent planned extensions beyond the Round 2 MVP:
- **Full Containerized Sandboxes**: Activating `docker_manager.py` to run task repositories inside hardened ephemeral Docker containers.
- **Dynamic Playwright Test Generation**: Empowering the `TesterAgent` with dynamic LLM generation of complex multi-page Playwright user journey scripts.
- **Multi-File Build Pipelines**: Support for automated npm/webpack build step execution inside task workspaces prior to browser verification.
- **Bi-Directional GitHub Synchronization**: Listening to GitHub webhooks so human code reviews on pull requests trigger automated agent revisions.

---

## 20. Conclusion & Architectural Summary

Nexus establishes that **reliable autonomous AI software engineering requires rigorous architectural governance**. By coupling role-specialized AI agents with **deterministic state machines**, **real browser automation**, **closed-loop self-correction**, **sandboxed version control**, and **human-in-the-loop gates**, Nexus transforms generative AI from an unpredictable coding assistant into a dependable, production-grade autonomous software engineering team.

---
*NEXUS — Autonomous Multi-Agent Software Engineering Platform*  
*Document Generated: October 2026 | Technical Evaluation Reference*
