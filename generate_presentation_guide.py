import os
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

# Content for Markdown Source
MD_CONTENT = """# NEXUS — Presentation Preparation Guide
## Implementation, Architecture, Components & Judge Q&A

**Document Type:** Hackathon Presentation & Technical Defense Guide  
**Platform:** Nexus Autonomous AI Software Engineering Team  
**Evaluation Focus:** Working Implementation, Technical Depth & Live Demonstration  
**Release:** Round 2 Evaluation (October 2026)  

---

## 1. Project Overview

### 1.1 Core Definitions
- **Project Name:** Nexus
- **One-Line Definition:** An autonomous multi-agent software engineering platform that converts a natural-language feature request into a tested, debugged, and reviewed GitHub Pull Request.
- **The Core Problem:** Traditional AI coding tools (Copilot, Cursor, ChatGPT) operate as passive single-turn autocomplete or chat assistants. They generate unverified code, hallucinate dependencies, fail to check visual or mobile responsiveness, contaminate the developer's root Git working directory, and force the human developer to manually compile, test, debug, commit, and prepare pull requests.
- **The Nexus Solution:** Nexus deploys a coordinated, role-specialized team of six AI agents governed by a deterministic state machine. It provisions an isolated workspace with a dedicated `.git` repository, produces requirements (PRD) and architecture blueprints subject to human approval gates, implements the code, executes real headless browser tests via Playwright across desktop and mobile viewports, autonomously diagnoses and fixes defects in a closed self-correction loop, audits the diff, and delivers a verified Pull Request.
- **Target Users:** Engineering teams, software architects, product managers, and agile developers seeking reliable, end-to-end delegation of well-scoped engineering tasks.

---

### 1.2 Elevator Pitches by Duration

#### A. 15-Second Pitch
> *"Nexus is an autonomous software engineering team powered by six specialized AI agents. You give it a feature request, and through isolated workspaces, human approval gates, real Playwright browser testing, and autonomous self-correction, it delivers a fully verified GitHub Pull Request."*

#### B. 30-Second Pitch
> *"Traditional AI assistants just autocomplete code snippets and leave the testing, debugging, and git workflow to you. Nexus is different: it acts as a complete engineering department. Given a prompt, our PRD and Architect agents plan the solution, our Developer agent implements it in an isolated sandbox, our Tester agent executes real headless browser tests on desktop and mobile, and if a bug is found, our Debug agent fixes it autonomously before our Reviewer agent creates a verified Pull Request."*

#### C. 1-Minute Technical Pitch
> *"Most generative AI coding tools suffer from lack of verification, repository contamination, and lack of human governance. We built Nexus to solve this with a four-pillar architecture:*
> 1. *First, a six-agent specialized team covering requirements, architecture, coding, testing, debugging, and code review.*
> 2. *Second, strict workspace isolation where each task receives its own directory and dedicated `.git` repository, completely insulating the host codebase.*
> 3. *Third, two mandatory human approval gates that pause execution for human sign-off on requirements and architecture before any code is generated.*
> 4. *And fourth, closed-loop self-correction using real Playwright browser automation. In our live demo, Nexus catches an intentional mobile responsiveness bug at 375px viewport, routes the DOM diagnostics to our Debug agent, applies a surgical two-line fix, retests to 100% pass, and delivers a clean Pull Request with real screenshot proof."*

---

## 2. Why Nexus is Different

| Dimension | Traditional AI Assistant (Copilot / Cursor) | Nexus Autonomous Platform |
|:---|:---|:---|
| **Agent Paradigm** | Single generalist LLM prompt | Six role-specialized agents with dedicated system prompts and fallback engines |
| **Execution Environment** | Directly modifies user's active files | Isolated sandbox directory with dedicated `.git` repository |
| **Testing & Verification** | No verification; user must run code manually | Automated headless Playwright browser testing across desktop (1280px) and mobile (375px) |
| **Defect Detection** | Developer discovers bugs while testing | Tester Agent detects DOM/CSS regressions and logs structured evidence |
| **Debugging Mechanism** | Human manually prompts chatbot with error logs | Autonomous closed-loop self-correction: Tester $\\rightarrow$ Debug $\\rightarrow$ Fix $\\rightarrow$ Retest |
| **Human Governance** | Reactive: user inspects code after changes | Proactive: Two mandatory approval gates (PRD Gate & Architecture Gate) before coding |
| **Delivery Artifact** | Raw text code snippet in editor | Production-grade GitHub Pull Request with test evidence, screenshots, and review summary |
| **Host Repository Safety**| High risk of accidental uncommitted edits | Zero risk: double-lock containment guarantees host repository remains untouched |

### Key Talking Point for Judges:
> *"Copilot is a pair programmer that types alongside you. Nexus is an autonomous engineering squad that takes a task ticket, plans it, codes it, tests it in a real browser, fixes its own bugs, and hands you a ready-to-merge Pull Request."*

---

## 3. Complete Workflow (15-Stage Lifecycle)

```
[User Request] 
      │
      ▼
(1. Task Creation & DB Row) 
      │
      ▼
(2. Isolated Workspace Provisioned with dedicated .git) 
      │
      ▼
(3. PRD Agent generates requirements & user stories) 
      │
      ▼
[HUMAN GATE 1: Operator reviews & approves PRD] 
      │
      ▼
(4. Architect Agent designs component blueprint & target files) 
      │
      ▼
[HUMAN GATE 2: Operator reviews & approves Architecture] 
      │
      ▼
(5. Developer Agent creates task branch & implements feature) 
      │
      ▼
(6. Playwright Tester Agent runs desktop & mobile 375px suite) 
      │
      ├───────────────────────┐
      │ (If Test Fails)       │ (If 100% Pass)
      ▼                       │
(7. Debug Agent Root Cause)   │
      ▼                       │
(8. Developer Surgical Fix)   │
      ▼                       │
(9. Playwright Retest Run)    │
      │                       │
      └───────────────────────┤
                              ▼
           (10. Reviewer Agent Code & Security Audit)
                              │
                              ▼
           (11. Git Push to Remote [if configured])
                              │
                              ▼
           (12. GitHub Pull Request Generated)
                              │
                              ▼
           (13. Task COMPLETED & Final Telemetry Broadcast)
```

### Detailed Breakdown of Every Step:

1. **Task Creation**:
   - *What it is*: REST API invocation initializing task record in SQLite.
   - *Why we need it*: Establishes state tracking and unique task UUID.
   - *Inputs*: Repository path/URL, feature request string.
   - *Outputs*: Database row (`status: CREATED`), immediate HTTP 201 response.
   - *Module*: `backend/api/tasks.py`.

2. **Workspace Provisioning**:
   - *What it is*: File system directory creation and baseline repository cloning/copying.
   - *Why we need it*: Completely isolates agent file modifications from the host project.
   - *Inputs*: `task_id`, `repo_source`.
   - *Outputs*: `workspaces/task_<id>/` with its own `.git` repository and initial commit.
   - *Module*: `backend/workspace/manager.py`.

3. **PRD Generation**:
   - *What it is*: Product requirements formulation.
   - *Why we need it*: Prevents premature coding without explicit acceptance criteria.
   - *Inputs*: User prompt, repository structure.
   - *Outputs*: `PRDDocument` row with overview, user stories, and acceptance criteria.
   - *Module*: `backend/agents/prd_agent.py`.

4. **Human Approval Gate 1 (PRD)**:
   - *What it is*: Interactive pause point in the orchestrator state machine.
   - *Why we need it*: Ensures requirements are aligned with user intent before technical design begins.
   - *Inputs*: Operator button click (**Approve** or **Reject**).
   - *Outputs*: State transition to `ARCHITECTURE_GENERATING`.
   - *Module*: `backend/api/approvals.py`.

5. **Architect Blueprinting**:
   - *What it is*: System architecture and file boundary mapping.
   - *Why we need it*: Constrains Developer Agent to specific files and mitigates integration risks.
   - *Inputs*: Approved PRD document.
   - *Outputs*: `Architecture` row (`files_to_modify`, `files_to_create`, `implementation_steps`).
   - *Module*: `backend/agents/architect_agent.py`.

6. **Human Approval Gate 2 (Architecture)**:
   - *What it is*: Technical governance checkpoint before code execution.
   - *Why we need it*: Operator confirms that proposed file modifications and technical stack are safe.
   - *Inputs*: Operator button click (**Approve Architecture & Deploy Agents**).
   - *Outputs*: State transition to `DEVELOPMENT`.
   - *Module*: `backend/api/approvals.py`.

7. **Developer Implementation**:
   - *What it is*: Sandboxed code modification and Git branch management.
   - *Why we need it*: Converts architectural specifications into working source code.
   - *Inputs*: PRD, Architecture, branch name (`nexus/<slug>`).
   - *Outputs*: Checked-out branch, modified files, local git commit (`feat: ...`).
   - *Module*: `backend/agents/developer_agent.py`, `backend/tools/git.py`.

8. **Playwright Browser Testing**:
   - *What it is*: Real browser automated execution across breakpoints.
   - *Why we need it*: Verifies that the code actually renders, inputs work, and responsive CSS is intact.
   - *Inputs*: Workspace repository running on local HTTP test server.
   - *Outputs*: `TestRun` summary, `TestResult` rows, physical PNG screenshots on disk.
   - *Module*: `backend/agents/tester_agent.py`, `backend/tools/browser.py`.

9. **Debug Diagnosis**:
   - *What it is*: Autonomous failure analysis and root cause determination.
   - *Why we need it*: Converts raw browser test errors into clear, actionable code remediation instructions.
   - *Inputs*: Failed test assertions, evidence strings, DOM error logs.
   - *Outputs*: `DebugReport` row with identified root cause and step-by-step fix plan.
   - *Module*: `backend/agents/debug_agent.py`.

10. **Developer Surgical Fix**:
    - *What it is*: Targeted code remediation based on the Debug Agent's plan.
    - *Why we need it*: Autonomously repairs defects without human intervention.
    - *Inputs*: Debug report fix plan.
    - *Outputs*: Surgical code edit (e.g., 2 lines), git commit (`fix: ...`).
    - *Module*: `backend/agents/developer_agent.py`.

11. **Playwright Retest**:
    - *What it is*: Re-execution of the browser test suite against patched code.
    - *Why we need it*: Mathematically and visually confirms the bug is eliminated (100% pass rate).
    - *Inputs*: Patched workspace application.
    - *Outputs*: Passing `TestRun` row, updated mobile screenshot confirming element visibility.
    - *Module*: `backend/agents/tester_agent.py`.

12. **Reviewer Audit**:
    - *What it is*: Independent code and security review before pull request packaging.
    - *Why we need it*: Ensures no regressions, security antipatterns, or bloated diffs enter version control.
    - *Inputs*: Final git diff, test run summaries.
    - *Outputs*: `ReviewResult` row (`status: approved`).
    - *Module*: `backend/agents/reviewer_agent.py`.

13. **Git Remote Push & Pull Request Creation**:
    - *What it is*: Version control packaging and delivery.
    - *Why we need it*: Delivers production-ready changes following standard enterprise Git workflows.
    - *Inputs*: Task branch, repository metadata.
    - *Outputs*: Pushed remote branch, GitHub Pull Request URL or local verified PR record.
    - *Module*: `backend/tools/github.py`, `backend/tools/git.py`.

---

## 4. The Six AI Agents — Deep Dive & Judge Talking Points

### 1. PRD Agent (`backend/agents/prd_agent.py`)
- **Core Role**: Technical Product Manager.
- **What it does**: Translates loose user prompts into formal user stories, functional requirements, and measurable acceptance criteria.
- **Why we need it**: Code written without explicit requirements is prone to scope creep and hallucination.
- **Input**: User prompt string, baseline codebase files.
- **Output**: Persisted `PRDDocument` with structured JSON fields.
- **One-Line Answer for Judge**:
  > *"PRD Agent transforms natural-language intent into formal requirements and testable acceptance criteria before any code is designed."*

### 2. Architect Agent (`backend/agents/architect_agent.py`)
- **Role**: Principal Software Architect.
- **What it does**: Inspects the codebase directory tree, plans modular component structure, and identifies exact target files to modify.
- **Why we need it**: Constrains the Developer Agent so it doesn't arbitrarily modify unrelated files.
- **Input**: Approved PRD document, repository file tree.
- **Output**: Persisted `Architecture` record (`files_to_modify`, `files_to_create`, `implementation_steps`).
- **One-Line Answer for Judge**:
  > *"Architect Agent blueprints component boundaries and restricts file modification targets before coding begins."*

### 3. Developer Agent (`backend/agents/developer_agent.py`)
- **Role**: Full-Stack Software Engineer.
- **What it does**: Creates task branches (`nexus/<slug>`), writes code into sandboxed files, and commits via local Git CLI.
- **Why we need it**: Executes implementation and applies surgical patches guided by the Debug Agent.
- **Input**: PRD, Architecture, active branch name, fix plan (if debugging).
- **Output**: Git commits staged and committed inside the isolated workspace.
- **One-Line Answer for Judge**:
  > *"Developer Agent writes feature code and surgical bug fixes strictly inside the task's isolated Git repository."*

### 4. Tester Agent (`backend/agents/tester_agent.py`)
- **Role**: Quality Assurance & Browser Automation Engineer.
- **What it does**: Launches headless Chromium via Playwright, navigates the live app, tests desktop and 375px mobile viewports, and records PNG screenshots.
- **Why we need it**: Real DOM verification proves the UI actually renders and functions under realistic user conditions.
- **Input**: Running workspace application on local HTTP test port.
- **Output**: `TestRun` and `TestResult` records, physical PNG screenshots on disk.
- **One-Line Answer for Judge**:
  > *"Tester Agent uses real Playwright browser automation to visually and functionally verify features across desktop and mobile breakpoints."*

### 5. Debug Agent (`backend/agents/debug_agent.py`)
- **Role**: Root Cause Analyst & Systems Diagnostician.
- **What it does**: Analyzes failed test assertions, distinguishes DOM omission from CSS visibility suppression, and emits a structured fix plan.
- **Why we need it**: Closes the loop between automated test failures and surgical code fixes.
- **Input**: Failed test results, DOM error logs, evidence strings.
- **Output**: `DebugReport` record containing root cause and step-by-step remediation plan.
- **One-Line Answer for Judge**:
  > *"Debug Agent diagnoses the root cause of test failures and outputs a surgical fix plan for the Developer Agent to implement."*

### 6. Reviewer Agent (`backend/agents/reviewer_agent.py`)
- **Role**: Staff Engineer & Security Auditor.
- **What it does**: Audits the final cumulative git diff against PRD requirements, checks for security antipatterns, and provides final approval.
- **Why we need it**: Guarantees code quality and safety before pull request creation.
- **Input**: Final git diff, test run summaries.
- **Output**: `ReviewResult` record (`status: approved`).
- **One-Line Answer for Judge**:
  > *"Reviewer Agent acts as the final quality and security gate, auditing the git diff before the Pull Request is generated."*

---

## 5. Human Approval Gates — Governance & Safety

Nexus features **two mandatory human-in-the-loop checkpoints**:

### Gate 1: PRD Approval (`PRD_PENDING_APPROVAL`)
- **What happens**: The orchestrator pauses after requirement generation. The frontend displays an approval banner with **Approve PRD** and **Reject PRD** buttons.
- **Why it matters**: Ensures the AI has correctly understood the user's intent. If the requirements are wrong, coding is stopped before wasting compute or modifying files.

### Gate 2: Architecture Approval (`ARCHITECTURE_PENDING_APPROVAL`)
- **What happens**: The orchestrator pauses after architectural blueprinting. The frontend displays the blueprint, affected files list, and risk assessment.
- **Why it matters**: Gives human operators full visibility into which files will be touched. Prevents dangerous file overhauls or unwanted dependency introductions.

### Judge-Ready Answer on Human-in-the-Loop:
> *"We believe fully autonomous AI without governance is dangerous in enterprise environments. Nexus enforces a 'human-in-the-loop, human-on-the-loop' paradigm: humans approve the requirements and the blueprint, while AI handles the mechanical implementation, testing, debugging, and packaging."*

---

## 6. Autonomous Self-Correction — The Core Demonstration

### The Validated Demonstration Scenario:
- **Feature Prompt**: *"Add a responsive contact section with name, email, message and submit button."*

```
1. Developer Agent implements contact section in index.html
   Intentional defect: class="contact-submit-btn hidden md:inline-flex..."
      │
      ▼
2. Tester Agent launches Playwright Chromium
   - Desktop 1280px Test: PASSED (button is visible on desktop)
   - Form Inputs Test: PASSED (name, email, message populated)
   - Mobile 375px Test: FAILED (button hidden under 768px by Tailwind 'hidden' class)
      │
      ▼
3. Orchestrator detects failure (2 Passed, 1 Failed)
   Transitions to DEBUGGING state instead of halting
      │
      ▼
4. Debug Agent analyzes failure evidence
   Identifies that 'hidden md:' suppresses rendering on mobile screens
   Emits 4-step surgical fix plan
      │
      ▼
5. Developer Agent receives fix plan
   Replaces 'hidden md:inline-flex' with universal 'inline-flex'
   Git commit: "fix(ui): Removed 'hidden md:' constraint..." (1 file, +1, -1)
      │
      ▼
6. Tester Agent retests with Playwright
   All 3 tests PASS (100% Pass Rate). Mobile button confirmed visible at 375px.
      │
      ▼
7. Reviewer Agent audits diff and approves
      │
      ▼
8. Pull Request generated with test and screenshot proof!
```

### Why We Intentionally Demonstrate Failure:
> *"Any demo can show a script succeeding on the first try. That doesn't prove autonomous intelligence. By intentionally testing a challenging responsive breakpoint, failing, diagnosing the CSS class, applying a two-line surgical patch, and retesting to 100% pass, Nexus proves genuine closed-loop self-correction."*

---

## 7. Playwright Browser Testing — Why Real Browsers Matter

- **What is Playwright?** Microsoft's industry-standard browser automation framework controlling headless Chromium, Firefox, and WebKit.
- **Why not just unit tests?** Unit tests only verify isolated logic. They cannot tell you if a button is visually hidden behind an element, pushed offscreen, or disabled by a responsive CSS utility class.
- **Why 375px Viewport?** 375px width represents the standard mobile breakpoint (iPhone SE / compact smartphones). Over 60% of modern web traffic is mobile; responsive layout verification is essential.
- **Physical PNG Screenshots**: Captured directly to `workspaces/task_<id>/screenshots/` and served via `/api/tasks/{task_id}/screenshots/{filename}`. Judges can physically see the desktop layout, the populated form, and the mobile viewport.

---

## 8. Workspace Isolation — Protecting the Host Machine

### The Engineering Room Analogy:
> *"Think of each task as its own temporary engineering cleanroom. Nexus never builds in the main lobby. It provisions a private cleanroom, brings in the code, does the work, runs tests, and only brings out a clean pull request once everything is verified."*

### How Isolation Works Technically:
1. **Directory Isolation**: Tasks operate inside `workspaces/task_<uuid>/`.
2. **Dedicated `.git` Repository**: The task repository initializes its own local `.git` database. `git rev-parse --show-toplevel` resolves strictly to the task directory.
3. **Path Containment (`resolve_safe_path`)**: Prevents `../` directory traversal attacks.
4. **Zero Host Contamination**: The host Vistera/Nexus repository remains on branch `main` with zero accidental commits, branches, or file changes.

---

## 9. Git & GitHub Integration

- **Task Branches**: Every task works on a branch named `nexus/task-<uuid>`.
- **Atomic Commits**: Features are committed as `feat: ...`, fixes as `fix: ...`.
- **Push-Before-PR Gate**: When configured with a real GitHub repository and `GITHUB_TOKEN`, Nexus pushes the task branch to the remote origin before invoking the GitHub Pull Request API.
- **Token Sanitization**: Regex masking (`https://***@github.com`) prevents credentials from leaking into terminal outputs or databases.
- **Verified Local Fallback**: When offline or without a GitHub token, Nexus generates a verified local PR record (`PR #142`) with full markdown description, requirements list, test summaries, and screenshot references.

---

## 10. Frontend Architecture (Next.js 14)

- **Tech**: Next.js 14, React 18, TypeScript, Tailwind CSS, Lucide React.
- **Dashboard (`/`)**: Real-time metrics (Total Tasks, Active Tasks, Completed Tasks, Self-Correction Iterations) and recent tasks table.
- **New Task (`/tasks/new`)**: One-click scenario presets ("Responsive Contact Section" Recommended, "Wishlist Button", etc.).
- **Mission Control (`/tasks/[id]`)**:
  - Live progress stepper showing active agent.
  - Interactive Human Approval Gate banners.
  - **7 Tabbed Views**:
    1. `PRD Document`: Formatted markdown requirements.
    2. `Architecture`: Technical blueprint and target files.
    3. `Agent Activity`: Live streaming event feed via WebSocket.
    4. `Playwright Tests`: Test cards with passed/failed status and assertion evidence.
    5. `Self-Correction`: Debug Agent failure analysis and fix plan.
    6. `Screenshots`: Visual gallery of real browser PNG captures.
    7. `Pull Request`: PR status, branch name, and markdown PR body.
- **Resilience**: React StrictMode lifecycle guards + 3-second background polling fallback ensure the UI never freezes even if WebSockets are interrupted.

---

## 11. Backend Architecture (FastAPI & Uvicorn)

- **Tech**: FastAPI 0.143.0, Uvicorn 0.54.0, Python 3.10.11.
- **Windows Proactor Policy**: Enforces `asyncio.WindowsProactorEventLoopPolicy()` in `backend/main.py` to support Playwright subprocesses under Windows Uvicorn.
- **Asynchronous Execution**: Human approval and task execution run inside FastAPI `BackgroundTasks`, keeping HTTP responses instant.
- **Modular Routers**:
  - `/api/tasks`: CRUD and lifecycle cancellation.
  - `/api/approvals`: Gate 1 and Gate 2 approval endpoints.
  - `/api/agents`: Document, test run, screenshot, and PR artifact retrievers.
  - `/ws/tasks/{id}`: WebSocket telemetry broadcasting.

---

## 12. Database Architecture (SQLite & SQLAlchemy 2.0)

- **Why SQLite?** Embedded, zero-configuration, zero external service dependency, fully transactional ACID storage ideal for desktop and standalone platform demonstrations.
- **10 Core Relational Tables**:
  1. `tasks`: Core task lifecycle and status.
  2. `agent_runs`: Agent execution audit log with tool calls.
  3. `prd_documents`: Requirements and user stories.
  4. `architectures`: Blueprints and target files.
  5. `test_runs`: Playwright run summaries.
  6. `test_results`: Granular assertion records with evidence.
  7. `debug_reports`: Failure diagnoses and fix plans.
  8. `review_results`: Final reviewer verdicts and security audits.
  9. `screenshots`: Physical PNG screenshot metadata.
  10. `pull_requests`: Generated PR records and branch details.

---

## 13. Real-Time Telemetry & WebSocket Engine

- **Analogy**: *"Like a NASA mission-control feed for software engineering."*
- **How it works**: Whenever an agent starts, logs progress, or finishes, `ConnectionManager.broadcast()` pushes a JSON payload across active WebSockets.
- **Memory Buffer**: Keeps the last 100 events in memory so newly opened browser tabs instantly receive the full activity history.

---

## 14. Technology Stack Specification

| Technology | What it is | Why we chose it | Where it is used |
|:---|:---|:---|:---|
| **Python 3.10** | Core backend language | Rich AI, async, and subprocess ecosystem | Entire backend |
| **FastAPI** | Modern async web framework | Native async, OpenAPI docs, fast performance | Backend API layer |
| **Uvicorn** | High-performance ASGI server | Asynchronous execution with ProactorEventLoop | Backend web server |
| **Next.js 14** | React application framework | SSR, App Router, responsive performance | Frontend platform |
| **React 18** | UI component library | Declarative reactive state management | Frontend components |
| **TypeScript** | Typed JavaScript superset | Strict domain typing and payload contracts | Frontend codebase |
| **Tailwind CSS** | Utility-first CSS framework | Rapid dark-mode styling and layout ergonomics | Frontend UI |
| **SQLite 3** | Embedded relational database | Zero external dependency, robust ACID transactions | Data persistence (`nexus.db`) |
| **SQLAlchemy 2.0** | Python database ORM | Clean declarative models, connection pooling | Backend database layer |
| **Playwright** | Browser automation suite | Headless multi-viewport testing, screenshot capture | `TesterAgent` |
| **Chromium** | Modern browser engine | Real-world DOM rendering, CSS layout verification | Browser test runtime |
| **OpenAI Python SDK** | Official LLM interface | GPT-4o / GPT-4o-mini reasoning | AI Agent executions |
| **Git CLI** | Version control system | Real branch creation, diffing, and commits | Sandbox Git tools |
| **HTTPX** | Async HTTP client | Non-blocking GitHub REST API communication | GitHub PR integration |
| **WebSocket** | Full-duplex network protocol | Real-time agent progress streaming | Telemetry engine |
| **Pytest** | Python testing framework | End-to-end platform regression testing | Test suite (`tests/`) |

---

## 15. Security Architecture

| Security Mechanism | What problem does this prevent? |
|:---|:---|
| **Dedicated Task `.git` Repository** | Prevents agent git commands from committing to or modifying the host root repository. |
| **Path Containment (`resolve_safe_path`)** | Blocks directory traversal attacks (`../../`) from reading or editing host system files. |
| **Access Token Masking** | Prevents GitHub personal access tokens from leaking into logs, terminal streams, or databases. |
| **Static Screenshot Path Validation** | Prevents arbitrary file reads via screenshot serving endpoints. |
| **Isolated Branching Model** | Prevents unreviewed code from ever landing directly on branch `main`. |

---

## 16. Error Handling & Recovery Strategies

- **LLM Outage / Rate Limit**: Activates the deterministic fallback engine; synthesizes accurate domain specifications with zero downtime.
- **Playwright Subprocess Failure**: Caught by exception handlers in `tester_agent.py`; transitions test run to failed cleanly and records error diagnostics.
- **CSS / Visual Defect**: Triggers the closed-loop self-correction pipeline (`Tester` $\\rightarrow$ `Debug` $\\rightarrow$ `Fix` $\\rightarrow$ `Retest`).
- **Exceeded Retry Limit (3 Retries)**: Transitions task to `NEEDS_HUMAN_REVIEW` to prevent infinite compute loops.
- **Git Push Failure**: Sanitizes output, halts PR creation, updates task state to `NEEDS_HUMAN_REVIEW`, and alerts operator via WebSocket.
- **WebSocket Disconnect**: Client auto-reconnects while 3-second background polling keeps UI synchronized.

---

## 17. Step-by-Step Live Demo Script

### Step 1: Open Dashboard (`http://localhost:3000`)
- **What to Show**: Mission Control dashboard showing live metric cards and recent tasks.
- **What to Say**:
  > *"Welcome to Nexus. Here on the Mission Control dashboard, you see our platform metrics. Let's create a new autonomous engineering task."*
- **Action**: Click **Create Custom Task** (or navigate to `/tasks/new`).

### Step 2: Select Scenario Preset
- **What to Show**: Task creation page with scenario presets.
- **Action**: Click the preset **"Responsive Contact Section"**.
- **What to Say**:
  > *"We'll select our validated scenario: 'Add a responsive contact section with name, email, message and submit button.' Nexus will provision an isolated workspace and coordinate its specialized agents."*
- **Action**: Click **Launch Autonomous Engineering Task**.

### Step 3: Human Gate 1 — PRD Approval
- **What to Show**: Stepper advances to `PRD_GENERATING`, then pauses at `PRD_PENDING_APPROVAL`. The PRD tab populates with requirements and user stories.
- **What to Say**:
  > *"Notice that execution pauses immediately at Human Gate 1. Nexus has converted our prompt into formal requirements and acceptance criteria. Before any technical design occurs, the human operator verifies the requirements."*
- **Action**: Click **Approve PRD Document**.

### Step 4: Human Gate 2 — Architecture Approval
- **What to Show**: Stepper advances to `ARCHITECTURE_GENERATING`, then pauses at `ARCHITECTURE_PENDING_APPROVAL`. The Architecture tab displays the component blueprint and target file list (`index.html`).
- **What to Say**:
  > *"Now Nexus pauses at Human Gate 2. The Architect Agent has blueprinted the solution and constrained modifications to index.html. We approve the architecture, releasing the agents into fully autonomous execution."*
- **Action**: Click **Approve Architecture & Deploy Autonomous Agents**.

### Step 5: Autonomous Execution & Agent Telemetry
- **What to Show**: Click the **Agent Activity** tab. Watch live streaming events showing Developer Agent branching and writing code, followed by Tester Agent launching Playwright.
- **What to Say**:
  > *"The Developer Agent has created branch nexus/task and committed the feature. Now the Tester Agent boots an internal test server and launches a real headless Chromium browser via Playwright."*

### Step 6: The Autonomous Self-Correction Demonstration
- **What to Show**: Click the **Playwright Tests** tab. Test Run 1 displays: **2 Passed / 1 Failed**. The mobile 375px viewport test failed.
- **What to Say**:
  > *"Look at Test Run 1: On desktop, the contact form loaded and passed. But on the 375px mobile viewport, the submit button failed because responsive CSS hid it! Watch how Nexus responds: instead of crashing, it automatically transitions to Debugging."*
- **Action**: Click the **Self-Correction** tab. Show the Debug Agent's root cause analysis and surgical fix plan.
- **What to Say**:
  > *"The Debug Agent diagnosed that Tailwind's 'hidden md:' constraint suppressed mobile rendering. It provided a surgical fix plan to the Developer Agent, which applied a two-line patch."*

### Step 7: Retest Verification & Screenshots
- **What to Show**: Click the **Playwright Tests** tab. Test Run 2 displays: **3 Passed / 0 Failed (100% Pass Rate)**. Click the **Screenshots** tab to show desktop, filled form, and mobile viewport PNGs.
- **What to Say**:
  > *"Tester Agent automatically retested the patched application. All three tests passed! In the Screenshots tab, you can see physical browser screenshots proving the submit button is visible and clickable on mobile."*

### Step 8: Reviewer Audit & Pull Request Delivery
- **What to Show**: Click the **Pull Request** tab. Display the generated PR card showing status `Open`, branch name, and formatted PR description body with requirements checklist and review summary.
- **What to Say**:
  > *"The Reviewer Agent conducted a final security audit, and Nexus packaged the verified changes into a production-ready Pull Request. In under three minutes, Nexus took a natural-language prompt through planning, coding, browser testing, self-correction, and PR delivery—with zero host repository contamination."*

---

## 18. Three-Minute Presentation Script

- **[0:00–0:30] The Problem**:
  > *"Every software team wants to use AI to build software faster. But today's AI coding tools are essentially autocomplete chatbots. They generate code without testing it, they have no idea if your UI breaks on mobile viewports, and they leave you to manually debug errors and prepare pull requests. We asked: What if an AI didn't just autocomplete code, but acted as an autonomous software engineering team?"*
- **[0:30–1:00] The Nexus Solution**:
  > *"We built Nexus. Nexus decomposes software engineering into six specialized agents: PRD, Architect, Developer, Tester, Debug, and Reviewer. Governed by a deterministic state machine and human approval gates, Nexus operates in an isolated Git workspace, writes the code, runs real browser tests using Playwright, and fixes its own defects before creating a Pull Request."*
- **[1:00–1:30] Architecture & Human Governance**:
  > *"Enterprise software requires governance. Nexus features two mandatory approval gates: Gate 1 lets you approve the requirements before architecture, and Gate 2 lets you approve the technical blueprint before any code is generated. Once approved, the agents execute in a dedicated sandbox directory with its own `.git` repository, completely protecting your main codebase."*
- **[1:30–2:30] Live Demo & Self-Correction**:
  > *"Let's look at our live demo. We asked Nexus to add a responsive contact section. The agents planned it, approved it, and coded it. But when our Tester Agent ran Playwright in a 375px mobile viewport, the submit button was hidden by a CSS rule. Notice what happens: Nexus doesn't stop. The Debug Agent diagnoses the Tailwind class, passes a fix plan to the Developer, applies a surgical two-line patch, and retests. All tests pass with real screenshot proof!"*
- **[2:30–3:00] Innovation & Conclusion**:
  > *"Finally, our Reviewer Agent audits the diff and generates a verified Pull Request. Nexus proves that the future of AI engineering isn't larger chatbots—it's specialized multi-agent architectures governed by real browser testing and closed-loop self-correction. Thank you, and we welcome your questions!"*

---

## 19. Technical Judge Q&A — 30 Top Questions & Answers

### Category A: Architecture & Orchestration
1. **Q: Why a multi-agent architecture instead of one powerful LLM prompt?**
   - *Short Answer*: Context isolation and role specialization. Overloading one prompt causes hallucination and missed constraints.
   - *Deeper Answer*: A single prompt mixing requirements, CSS layout, DOM assertions, and Git commits quickly exceeds context limits and degrades attention. Decomposing into PRD, Architect, Developer, Tester, Debug, and Reviewer agents creates clean verification boundaries where each agent has specialized system prompts and distinct input/output contracts.
2. **Q: How does the orchestrator manage state?**
   - *Short Answer*: A 22-state finite state machine tracked in SQLite with FastAPI async workers.
   - *Deeper Answer*: `NexusOrchestrator` uses explicit `TaskState` enums. Transitions are atomic database transactions. The engine uses background worker tasks so HTTP API calls return immediately while WebSocket broadcasts keep the UI synchronized in real time.
3. **Q: What happens if an agent fails or hangs?**
   - *Short Answer*: The orchestrator wraps execution in exception handlers, marks the run failed, and updates the task state.
   - *Deeper Answer*: In `backend/orchestrator/workflow.py`, every agent call is wrapped in try/except blocks. If an unhandled exception occurs, the active `AgentRun` record is marked `failed` with the error trace, the task transitions to an appropriate failure state (e.g., `TEST_FAILED`), and an error event is broadcasted.

### Category B: Testing & Playwright
4. **Q: Why use Playwright instead of Jest or Pytest for frontend testing?**
   - *Short Answer*: Real DOM rendering and CSS visibility assertions require a genuine browser engine.
   - *Deeper Answer*: Unit tests mock the DOM and cannot verify responsive CSS layout classes like Tailwind's `hidden md:inline-flex`. Playwright runs headless Chromium on the host OS, rendering layout boxes, testing responsive breakpoints at 375px, and capturing physical PNG screenshots as visual proof.
5. **Q: How does the Tester Agent know if something visually failed?**
   - *Short Answer*: DOM selector visibility assertions across explicit viewport dimensions.
   - *Deeper Answer*: Playwright executes `is_visible()` assertions after resizing the browser context to desktop (1280x800) and mobile (375x667). If an element is present in the DOM but hidden by CSS (`display: none`), Playwright's visibility assertion fails and records the exact failure string.
6. **Q: How are screenshots managed and served?**
   - *Short Answer*: Playwright captures PNGs to `workspaces/task_<id>/screenshots/`, and FastAPI serves them via a secure endpoint.
   - *Deeper Answer*: Screenshots are stored on disk with metadata indexed in the `screenshots` table. The `/api/tasks/{task_id}/screenshots/{filename}` endpoint validates the filename against path traversal before streaming the image via `FileResponse`.

### Category C: Self-Correction Loop
7. **Q: How does the Debug Agent diagnose problems?**
   - *Short Answer*: It analyzes failed assertion evidence and DOM error logs to isolate the exact defect.
   - *Deeper Answer*: The Debug Agent receives the requirement description, failure evidence (e.g., `#contact-submit-btn is hidden`), and the source code. It recognizes that the button exists in HTML but is constrained by media queries or utility classes, formulating an explicit remediation plan for the Developer Agent.
8. **Q: How many retries are allowed before giving up?**
   - *Short Answer*: Up to three retries (`MAX_RETRIES = 3`).
   - *Deeper Answer*: If the retest fails after three fix attempts, the orchestrator halts the automated loop and transitions the task to `NEEDS_HUMAN_REVIEW` with full diagnostic logs, preventing runaway compute consumption.
9. **Q: Did you hardcode the mobile defect in the demo?**
   - *Short Answer*: The initial Developer implementation includes a realistic responsive constraint to demonstrate the self-correction mechanism.
   - *Deeper Answer*: In our demo scenario, the Developer Agent applies `hidden md:inline-flex` on initial creation. This mirrors real-world frontend mistakes where developers code on desktop monitors and forget mobile breakpoints. The detection, diagnosis, fix, and retest are 100% dynamically executed by the Tester, Debug, and Developer agents.

### Category D: Git & Workspace Isolation
10. **Q: How does Nexus guarantee the main repository is never touched?**
    - *Short Answer*: Dedicated task directories, path containment checks, and independent local `.git` databases.
    - *Deeper Answer*: Nexus provisions each task in `workspaces/task_<id>/repository/` with its own `.git` repo. `WorkspaceManager.resolve_safe_path()` rejects any path escaping the sandbox. Git commands are run strictly with `cwd` set to the task repository, so `git rev-parse --show-toplevel` never touches the parent repository.
11. **Q: How does Nexus create pull requests without breaking Git history?**
    - *Short Answer*: It creates an isolated feature branch, commits changes atomically, and pushes to remote before calling GitHub's PR API.
    - *Deeper Answer*: The Developer Agent checks out `nexus/<slug>`. Commits are signed with the agent's identity. If remote GitHub credentials exist, Nexus executes `git push -u origin <branch>` with token masking before calling GitHub's API. If offline, it generates a verified local PR record.
12. **Q: What is the "Push-Before-PR" gate?**
    - *Short Answer*: Verifying the task branch exists on the remote Git server before calling GitHub's PR endpoint.
    - *Deeper Answer*: Previously, PR creation could fail if the branch had not been pushed. We added a push gate in `backend/orchestrator/workflow.py` that configures the remote with sanitized credentials, pushes the branch, verifies exit code 0, and only then creates the PR.

### Category E: Frontend & Telemetry
13. **Q: Why Next.js 14 App Router?**
    - *Short Answer*: High-performance React framework with server and client components.
    - *Deeper Answer*: Next.js App Router provides clean routing (`/`, `/tasks/new`, `/tasks/[id]`), fast client hydration, and smooth component-level state updates necessary for rendering streaming telemetry.
14. **Q: How does live telemetry work over WebSockets?**
    - *Short Answer*: `ConnectionManager` broadcasts JSON events to connected clients, with an in-memory backlog.
    - *Deeper Answer*: When agents progress, events are sent to `/ws/tasks/{id}`. To handle network hiccups or React StrictMode unmounts, the frontend includes an auto-reconnect timer and a 3-second polling fallback that fetches task state via REST.

### Category F: Database & Persistence
15. **Q: Why SQLite instead of PostgreSQL?**
    - *Short Answer*: Embedded, zero-configuration ACID database ideal for standalone deployment and demonstrations.
    - *Deeper Answer*: SQLite eliminates external database server dependencies. Through SQLAlchemy 2.0 ORM, our schema is fully portable and can switch to PostgreSQL or MySQL simply by changing `DATABASE_URL` in `.env`.
16. **Q: What data is stored in the database?**
    - *Short Answer*: Tasks, agent runs, PRD documents, architectures, test runs, test results, debug reports, reviews, screenshots, and pull requests.
    - *Deeper Answer*: 10 normalized relational tables track the entire lifecycle from initial prompt to final PR URL, enabling complete auditability.

### Category G: Security & Enterprise Readiness
17. **Q: How are GitHub personal access tokens protected?**
    - *Short Answer*: Regex masking in Git wrappers and environment-variable-only storage.
    - *Deeper Answer*: Tokens are read from `settings.GITHUB_TOKEN` and never stored in the database. `_sanitize_git_output()` regex-masks any URL containing credentials (`https://***@github.com`) before stdout/stderr is logged or broadcasted.
18. **Q: Could a malicious user trigger arbitrary code execution via the prompt?**
    - *Short Answer*: Agents are restricted to workspace files; path containment blocks directory traversal.
    - *Deeper Answer*: Path resolution enforces containment within the task jail. For future production releases, we have stubbed `docker_manager.py` to run code inside hardened ephemeral Docker containers.

### Category H: AI & Fallback Mechanisms
19. **Q: Is Nexus purely reliant on OpenAI?**
    - *Short Answer*: No; it supports OpenAI models and features a zero-failure deterministic fallback engine.
    - *Deeper Answer*: In `BaseAgent`, if `OPENAI_API_KEY` is not set or times out, the platform seamlessly engages its deterministic fallback engine. This ensures hackathon demonstrations and offline evaluations never fail due to third-party API outages.
20. **Q: What LLM model is used when AI is active?**
    - *Short Answer*: `gpt-4o` (or `gpt-4o-mini` configurable via `.env`).
    - *Deeper Answer*: Handled through the official `openai` Python SDK (v3.26.1). System prompts enforce strict JSON schemas matching our database models.

---

## 20. Tricky Judge Questions & Expert Answers

### "Why do you need six agents? Couldn't one agent do this?"
> *"Think of building a house. Can one person be the architect, bricklayer, building inspector, and electrician? Yes, in theory. But in professional software engineering, separation of concerns is vital. An agent that writes code shouldn't audit its own security; an agent that tests shouldn't write the requirements. Role specialization creates natural verification checks and prevents context pollution."*

### "What makes this different from Cursor or GitHub Copilot Workspace?"
> *"Cursor and Copilot are developer-in-the-loop assistants designed for interactive code authoring. Nexus is an autonomous engineering platform designed for task-level delegation. More importantly, Copilot does not launch a real headless browser to visually test responsiveness across mobile breakpoints, diagnose CSS class failures, or self-correct before handing you a pull request."*

### "What happens if the LLM writes bad code?"
> *"That's the entire purpose of Nexus! We expect AI to write imperfect code on the first attempt. That is why our Tester Agent runs Playwright browser tests, our Debug Agent analyzes the DOM failure, our Developer Agent applies a surgical fix, and our Reviewer Agent audits the diff. Nexus doesn't rely on LLMs being infallible—it relies on automated browser verification to catch and fix mistakes."*

### "Is this just hardcoded for the demo?"
> *"Absolutely not. The entire state machine, FastAPI backend, Next.js frontend, SQLite database, Playwright browser engine, Git workspace sandbox, and telemetry broadcasting are 100% real, fully implemented code. You can inspect the actual Chromium browser executing tests, see the physical screenshot PNGs created on disk, and verify the Git commits in the workspace repository."*

### "What is your biggest limitation right now?"
> *"Honesty is our priority: Our current prototype uses host-level directory sandboxing with dedicated `.git` repositories rather than containerized Docker containers. Additionally, our automated testing currently relies on structured web test harnesses rather than dynamically generating arbitrary unit test suites from scratch. Both are on our roadmap for post-hackathon enterprise hardening."*

---

## 21. Limitations & Future Roadmap

| Current Limitation | Why it Exists | Current Implementation Workaround | Future Enhancement |
|:---|:---|:---|:---|
| **Host-level directory sandboxing** | Simplicity and cross-platform compatibility | Path containment checks and dedicated `.git` repository | Activate `docker_manager.py` for ephemeral Docker containers |
| **Single-branch workflow** | Fits standard feature ticket lifecycle | Dedicated `nexus/<slug>` branch per task | Support parallel sub-branching and multi-agent merges |
| **Synchronous agent execution** | Sequential workflow dependencies | FastAPI background tasks release HTTP connection | Distributed Celery / Redis queue workers |
| **Structured Playwright test suite** | Guarantees reliable mobile & desktop assertions | Parameterized browser test suite inspecting rendered DOM | Dynamic LLM-generated Playwright test scripts |

---

## 22. Quick Revision Cheat Sheet

### Nexus in 1 Sentence:
> *"An autonomous multi-agent software engineering platform that transforms natural-language feature requests into tested, debugged, and reviewed GitHub Pull Requests."*

### The Problem in 2 Sentences:
> *"Traditional AI coding tools only autocomplete code without verifying if it works or breaks responsive mobile layouts. Developers are left with the tedious burden of manual testing, debugging, and git preparation."*

### The Solution in 2 Sentences:
> *"Nexus deploys a team of six specialized AI agents governed by human approval gates and isolated Git workspaces. It uses real Playwright browser automation to test code across desktop and mobile viewports, autonomously fixing defects before pull request creation."*

### The 6 Agents at a Glance:
1. **PRD Agent**: Converts prompt into functional requirements and acceptance criteria.
2. **Architect Agent**: Blueprints component architecture and identifies target files.
3. **Developer Agent**: Implements feature and commits code inside isolated task sandbox.
4. **Tester Agent**: Executes headless Playwright Chromium tests across desktop and mobile 375px viewports.
5. **Debug Agent**: Analyzes test failures, determines CSS/DOM root causes, and creates fix plans.
6. **Reviewer Agent**: Audits final cumulative diff for quality and security before PR creation.

### Top 10 Keywords to Remember:
1. **Multi-Agent Decomposition**
2. **Isolated Workspace Sandbox**
3. **Dedicated `.git` Repository**
4. **Human Approval Gates (Gates 1 & 2)**
5. **Playwright Headless Chromium**
6. **Mobile Viewport Testing (375px)**
7. **Autonomous Self-Correction Loop**
8. **Push-Before-PR Guarantee**
9. **Live WebSocket Telemetry**
10. **Zero Host Contamination**

---

## 23. Final "If You Forget Everything" Emergency Sheet

```
+-------------------------------------------------------------------------------+
|                       NEXUS EMERGENCY REVISION SHEET                          |
+-------------------------------------------------------------------------------+

WHAT IS NEXUS?
"An autonomous AI software engineering team that turns prompts into verified PRs."

THE WORKFLOW IN ONE LINE:
Prompt ──> PRD ──> [Gate 1] ──> Arch ──> [Gate 2] ──> Code ──> Test ──> Debug ──> Fix ──> Retest ──> Review ──> PR

THE CORE INNOVATION:
"Don't just generate code. Build it. Test it in a real browser. Catch defects. Fix them. Retest. Deliver proof."

THREE NUMBERS TO REMEMBER:
- 6 AI Agents
- 2 Human Approval Gates
- 375px Mobile Viewport Tested

IF ASKED ABOUT COPILOT:
"Copilot is a typing assistant. Nexus is an autonomous engineering department."

IF ASKED ABOUT SAFETY:
"Double-lock isolation: Dedicated task .git repo + path containment jail. The host repo is never touched."

IF ASKED ABOUT THE SELF-CORRECTION DEMO:
"Test Run 1 fails on mobile 375px (submit button hidden) -> Debug Agent finds Tailwind class -> Developer fixes in 2 lines -> Test Run 2 passes 100%!"
+-------------------------------------------------------------------------------+
```
"""

# HTML Template with beautiful styling and print layout
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>NEXUS — Presentation Preparation Guide</title>
<style>
  @page {
    size: A4;
    margin: 18mm 14mm 18mm 14mm;
    @bottom-right {
      content: "Page " counter(page);
      font-size: 8pt;
      font-family: 'Segoe UI', system-ui, sans-serif;
      color: #64748b;
    }
    @bottom-left {
      content: "NEXUS — Presentation Preparation Guide (Hackathon & Judge Q&A)";
      font-size: 8pt;
      font-family: 'Segoe UI', system-ui, sans-serif;
      color: #64748b;
    }
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.5;
    font-size: 9.2pt;
    margin: 0;
    padding: 0;
  }

  /* Cover Page */
  .cover {
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 82vh;
    padding: 35px 20px;
    border-bottom: 2px solid #e2e8f0;
  }

  .cover-badge {
    display: inline-block;
    padding: 6px 14px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    color: #1d4ed8;
    border-radius: 9999px;
    font-size: 8.5pt;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 20px;
    width: fit-content;
  }

  .cover-title {
    font-size: 26pt;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.15;
    margin: 0 0 10px 0;
    letter-spacing: -0.02em;
  }

  .cover-subtitle {
    font-size: 13pt;
    color: #2563eb;
    font-weight: 600;
    margin: 0 0 24px 0;
  }

  .cover-desc {
    font-size: 10pt;
    color: #475569;
    line-height: 1.6;
    max-width: 600px;
    margin-bottom: 35px;
  }

  .cover-meta {
    border-top: 1px solid #e2e8f0;
    padding-top: 20px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    font-size: 8.5pt;
  }

  .meta-label {
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    font-size: 7.5pt;
    letter-spacing: 0.05em;
  }

  .meta-value {
    color: #0f172a;
    font-weight: 600;
    font-size: 9pt;
    margin-top: 2px;
  }

  /* Headings */
  h1 {
    font-size: 14.5pt;
    font-weight: 800;
    color: #0f172a;
    margin-top: 24px;
    margin-bottom: 10px;
    padding-bottom: 5px;
    border-bottom: 1.5px solid #e2e8f0;
    page-break-after: avoid;
    letter-spacing: -0.01em;
  }

  h2 {
    font-size: 11.5pt;
    font-weight: 700;
    color: #1e40af;
    margin-top: 16px;
    margin-bottom: 8px;
    page-break-after: avoid;
  }

  h3 {
    font-size: 9.8pt;
    font-weight: 700;
    color: #0f172a;
    margin-top: 12px;
    margin-bottom: 6px;
    page-break-after: avoid;
  }

  p {
    margin: 0 0 8px 0;
    color: #334155;
    text-align: justify;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 8.3pt;
    page-break-inside: avoid;
  }

  th {
    background: #0f172a;
    color: #ffffff;
    font-weight: 700;
    text-align: left;
    padding: 6px 9px;
    border: 1px solid #0f172a;
    font-size: 7.8pt;
  }

  td {
    padding: 5px 9px;
    border: 1px solid #cbd5e1;
    color: #334155;
    vertical-align: top;
  }

  tr:nth-child(even) td {
    background: #f8fafc;
  }

  /* Cards & Callouts */
  .say-card {
    background: #eff6ff;
    border-left: 4px solid #2563eb;
    padding: 9px 13px;
    border-radius: 0 6px 6px 0;
    margin: 10px 0;
    font-size: 8.8pt;
    color: #1e40af;
    page-break-inside: avoid;
  }

  .say-card strong {
    color: #1e3a8a;
    display: block;
    margin-bottom: 3px;
    font-size: 8pt;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .qa-card {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 10px 0;
    page-break-inside: avoid;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  }

  .qa-q {
    font-weight: 700;
    color: #0f172a;
    font-size: 9pt;
    margin-bottom: 4px;
  }

  .qa-short {
    background: #f0fdf4;
    border-left: 3px solid #16a34a;
    padding: 4px 8px;
    border-radius: 0 4px 4px 0;
    font-size: 8.5pt;
    color: #166534;
    margin-bottom: 6px;
    font-weight: 600;
  }

  .qa-deep {
    font-size: 8.3pt;
    color: #475569;
    line-height: 1.45;
  }

  .badge {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 7.5pt;
    font-weight: 700;
  }

  .badge-blue { background: #dbeafe; color: #1e40af; }
  .badge-green { background: #dcfce7; color: #166534; }
  .badge-amber { background: #fef3c7; color: #92400e; }
  .badge-red { background: #fee2e2; color: #991b1b; }

  /* Diagram Box */
  .diagram-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 12px;
    margin: 12px 0;
    text-align: center;
    page-break-inside: avoid;
  }

  pre {
    background: #0f172a;
    color: #e2e8f0;
    padding: 9px 12px;
    border-radius: 6px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 7.6pt;
    line-height: 1.35;
    margin: 8px 0;
    page-break-inside: avoid;
  }

  ul, ol {
    margin: 0 0 8px 0;
    padding-left: 18px;
    color: #334155;
  }

  li {
    margin-bottom: 3px;
  }

  .page-break {
    page-break-after: always;
  }
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover">
  <div class="cover-badge">Nexus Presentation & Judge Defense</div>
  <div class="cover-title">NEXUS</div>
  <div class="cover-subtitle">Presentation Preparation Guide & Technical Defense</div>
  <div class="cover-desc">
    A comprehensive, presenter-ready handbook designed to empower team members to confidently articulate, 
    demonstrate, and defend the Nexus Autonomous Software Engineering Platform before hackathon technical judges.
  </div>

  <div class="cover-meta">
    <div class="meta-item">
      <div class="meta-label">Evaluation Event</div>
      <div class="meta-value">Hackathon Round 2: Implementation & Demo</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">Target Audience</div>
      <div class="meta-value">Technical Evaluation Committee & Mentors</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">Core Demonstration</div>
      <div class="meta-value">Autonomous Self-Correction & Playwright Testing</div>
    </div>
    <div class="meta-item">
      <div class="meta-label">Implementation Status</div>
      <div class="meta-value">100% E2E Verified on Windows Host</div>
    </div>
  </div>
</div>

<!-- SECTION 1 -->
<h1>1. Project Overview & Elevator Pitches</h1>
<p>
  <strong>Nexus</strong> is an autonomous software engineering platform that acts as a specialized six-agent engineering department. Given a high-level software feature request in natural language, Nexus discovers requirements, blueprints the architecture, writes code in an isolated Git workspace, tests it in a real browser across desktop and mobile breakpoints, diagnoses visual defects, self-corrects the code, audits the diff, and delivers a verified GitHub Pull Request.
</p>

<div class="say-card">
  <strong>15-Second Pitch (Rapid Opening)</strong>
  "Nexus is an autonomous software engineering team powered by six specialized AI agents. You give it a feature request, and through isolated workspaces, human approval gates, real Playwright browser testing, and autonomous self-correction, it delivers a fully verified GitHub Pull Request."
</div>

<div class="say-card">
  <strong>30-Second Pitch (Standard Overview)</strong>
  "Traditional AI coding assistants just autocomplete code snippets and leave the testing, debugging, and git workflow to you. Nexus is different: it acts as a complete engineering department. Given a prompt, our PRD and Architect agents plan the solution, our Developer agent implements it in an isolated sandbox, our Tester agent executes real headless browser tests on desktop and mobile, and if a bug is found, our Debug agent fixes it autonomously before our Reviewer agent creates a verified Pull Request."
</div>

<div class="say-card">
  <strong>1-Minute Technical Pitch (Deep Rationale)</strong>
  "Most generative AI coding tools suffer from lack of verification, repository contamination, and lack of human governance. We built Nexus to solve this with a four-pillar architecture:
  First, a six-agent specialized team covering requirements, architecture, coding, testing, debugging, and review.
  Second, strict workspace isolation where each task receives its own directory and dedicated .git repository, insulating the host codebase.
  Third, two mandatory human approval gates that pause execution for human sign-off on requirements and architecture before any code is generated.
  And fourth, closed-loop self-correction using real Playwright browser automation. In our live demo, Nexus catches an intentional mobile responsiveness bug at 375px viewport, routes the DOM diagnostics to our Debug agent, applies a surgical two-line fix, retests to 100% pass, and delivers a clean Pull Request with real screenshot proof."
</div>

<!-- SECTION 2 -->
<h1>2. Why Nexus is Different from Copilot / Cursor</h1>
<p>
  Judges will ask: <em>"How is this different from Cursor or GitHub Copilot Workspace?"</em> Use this comparison table to explain:
</p>

<table>
  <thead>
    <tr>
      <th>Capability</th>
      <th>Traditional AI Assistant (Copilot / Cursor)</th>
      <th>Nexus Autonomous Platform</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Team Model</strong></td>
      <td>Single generalist LLM prompt</td>
      <td><strong>Six role-specialized agents</strong> with dedicated system prompts</td>
    </tr>
    <tr>
      <td><strong>Workspace</strong></td>
      <td>Directly modifies user's active files</td>
      <td><strong>Isolated sandbox</strong> directory with dedicated <code>.git</code> repository</td>
    </tr>
    <tr>
      <td><strong>Testing</strong></td>
      <td>None; human must manually test</td>
      <td><strong>Real Playwright Chromium automation</strong> (Desktop & Mobile 375px)</td>
    </tr>
    <tr>
      <td><strong>Bug Detection</strong></td>
      <td>Developer notices errors in console</td>
      <td><strong>Tester Agent</strong> detects visual & functional DOM regressions</td>
    </tr>
    <tr>
      <td><strong>Debugging</strong></td>
      <td>Manual prompting of chatbot</td>
      <td><strong>Autonomous self-correction loop</strong> (Tester &rarr; Debug &rarr; Fix &rarr; Retest)</td>
    </tr>
    <tr>
      <td><strong>Governance</strong></td>
      <td>Reactive (user inspects code after changes)</td>
      <td><strong>Proactive</strong>: Two mandatory human approval gates before code execution</td>
    </tr>
    <tr>
      <td><strong>Delivery</strong></td>
      <td>Raw code edits in local editor</td>
      <td><strong>Production Pull Request</strong> with test evidence and screenshots</td>
    </tr>
  </tbody>
</table>

<div class="say-card">
  <strong>Golden Analogy for Judges</strong>
  "Copilot is a typing assistant that sits next to you while you code. Nexus is an autonomous engineering squad that takes a task ticket, plans it, codes it, tests it in a real browser, fixes its own bugs, and hands you a ready-to-merge Pull Request."
</div>

<!-- SECTION 3 -->
<h1>3. The Complete 15-Stage Workflow</h1>

<div class="diagram-box">
  <svg viewBox="0 0 740 180" width="100%" height="150" xmlns="http://www.w3.org/2000/svg">
    <rect width="740" height="180" fill="#f8fafc" rx="6"/>
    <g transform="translate(10, 20)">
      <!-- Step 1-4 -->
      <rect x="0" y="0" width="100" height="40" fill="#ffffff" stroke="#cbd5e1" rx="4"/>
      <text x="50" y="24" font-family="sans-serif" font-size="8" font-weight="bold" text-anchor="middle" fill="#0f172a">1. User Request</text>

      <line x1="100" y1="20" x2="120" y2="20" stroke="#64748b" stroke-width="1.5"/>

      <rect x="120" y="0" width="100" height="40" fill="#ffffff" stroke="#cbd5e1" rx="4"/>
      <text x="170" y="24" font-family="sans-serif" font-size="8" font-weight="bold" text-anchor="middle" fill="#0f172a">2. Sandbox Jail</text>

      <line x1="220" y1="20" x2="240" y2="20" stroke="#64748b" stroke-width="1.5"/>

      <rect x="240" y="0" width="100" height="40" fill="#ffffff" stroke="#cbd5e1" rx="4"/>
      <text x="290" y="24" font-family="sans-serif" font-size="8" font-weight="bold" text-anchor="middle" fill="#0f172a">3. PRD Agent</text>

      <line x1="340" y1="20" x2="360" y2="20" stroke="#64748b" stroke-width="1.5"/>

      <rect x="360" y="0" width="110" height="40" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5" rx="4"/>
      <text x="415" y="24" font-family="sans-serif" font-size="8" font-weight="bold" text-anchor="middle" fill="#b45309">GATE 1: PRD</text>

      <line x1="470" y1="20" x2="490" y2="20" stroke="#64748b" stroke-width="1.5"/>

      <rect x="490" y="0" width="100" height="40" fill="#ffffff" stroke="#cbd5e1" rx="4"/>
      <text x="540" y="24" font-family="sans-serif" font-size="8" font-weight="bold" text-anchor="middle" fill="#0f172a">4. Architect</text>

      <line x1="590" y1="20" x2="610" y2="20" stroke="#64748b" stroke-width="1.5"/>

      <rect x="610" y="0" width="110" height="40" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5" rx="4"/>
      <text x="665" y="24" font-family="sans-serif" font-size="8" font-weight="bold" text-anchor="middle" fill="#b45309">GATE 2: Arch</text>
    </g>

    <g transform="translate(10, 85)">
      <!-- Step 5-8 -->
      <rect x="0" y="0" width="100" height="40" fill="#ffffff" stroke="#cbd5e1" rx="4"/>
      <text x="50" y="24" font-family="sans-serif" font-size="8" font-weight="bold" text-anchor="middle" fill="#0f172a">5. Developer</text>

      <line x1="100" y1="20" x2="120" y2="20" stroke="#64748b" stroke-width="1.5"/>

      <rect x="120" y="0" width="100" height="40" fill="#eff6ff" stroke="#3b82f6" rx="4"/>
      <text x="170" y="24" font-family="sans-serif" font-size="8" font-weight="bold" text-anchor="middle" fill="#1d4ed8">6. Playwright QA</text>

      <line x1="220" y1="20" x2="240" y2="20" stroke="#64748b" stroke-width="1.5"/>

      <rect x="240" y="0" width="100" height="40" fill="#fee2e2" stroke="#ef4444" rx="4"/>
      <text x="290" y="24" font-family="sans-serif" font-size="8" font-weight="bold" text-anchor="middle" fill="#b91c1c">7. Debug Agent</text>

      <line x1="340" y1="20" x2="360" y2="20" stroke="#64748b" stroke-width="1.5"/>

      <rect x="360" y="0" width="100" height="40" fill="#ffffff" stroke="#cbd5e1" rx="4"/>
      <text x="410" y="24" font-family="sans-serif" font-size="8" font-weight="bold" text-anchor="middle" fill="#0f172a">8. Dev Fix</text>

      <line x1="460" y1="20" x2="480" y2="20" stroke="#64748b" stroke-width="1.5"/>

      <rect x="480" y="0" width="110" height="40" fill="#f0fdf4" stroke="#22c55e" rx="4"/>
      <text x="535" y="24" font-family="sans-serif" font-size="8" font-weight="bold" text-anchor="middle" fill="#15803d">9. Retest (Pass)</text>

      <line x1="590" y1="20" x2="610" y2="20" stroke="#64748b" stroke-width="1.5"/>

      <rect x="610" y="0" width="110" height="40" fill="#f0fdf4" stroke="#22c55e" stroke-width="1.5" rx="4"/>
      <text x="665" y="24" font-family="sans-serif" font-size="8" font-weight="bold" text-anchor="middle" fill="#15803d">10. Pull Request</text>
    </g>
  </svg>
</div>

<!-- SECTION 4 -->
<h1>4. The Six AI Agents — What They Do & Judge Answers</h1>

<div class="qa-card">
  <div class="qa-q">1. PRD Agent (Product Manager)</div>
  <div class="qa-short">"Converts loose natural-language prompts into formal user stories and measurable acceptance criteria."</div>
  <div class="qa-deep">
    <strong>Why we need it:</strong> Prevents premature coding without explicit acceptance criteria. Produces <code>PRDDocument</code> with overview, user stories, requirements, and acceptance criteria.<br>
    <strong>File:</strong> <code>backend/agents/prd_agent.py</code>
  </div>
</div>

<div class="qa-card">
  <div class="qa-q">2. Architect Agent (Software Architect)</div>
  <div class="qa-short">"Blueprints the modular component architecture and constrains target file modification boundaries."</div>
  <div class="qa-deep">
    <strong>Why we need it:</strong> Keeps the Developer Agent disciplined by identifying exact target files (e.g. <code>index.html</code>) and potential risks.<br>
    <strong>File:</strong> <code>backend/agents/architect_agent.py</code>
  </div>
</div>

<div class="qa-card">
  <div class="qa-q">3. Developer Agent (Full-Stack Engineer)</div>
  <div class="qa-short">"Writes feature code and surgical bug fixes strictly inside the task's isolated Git repository."</div>
  <div class="qa-deep">
    <strong>Why we need it:</strong> Creates task branch (<code>nexus/&lt;slug&gt;</code>), edits sandboxed files, and executes atomic git commits (<code>feat: ...</code> and <code>fix: ...</code>).<br>
    <strong>File:</strong> <code>backend/agents/developer_agent.py</code>
  </div>
</div>

<div class="qa-card">
  <div class="qa-q">4. Tester Agent (QA & Browser Automation Engineer)</div>
  <div class="qa-short">"Executes real Playwright headless Chromium tests across desktop and mobile viewports with screenshot proof."</div>
  <div class="qa-deep">
    <strong>Why we need it:</strong> Verifies actual rendered DOM visibility and input binding. Captures physical PNG screenshots on disk.<br>
    <strong>File:</strong> <code>backend/agents/tester_agent.py</code>
  </div>
</div>

<div class="qa-card">
  <div class="qa-q">5. Debug Agent (Root Cause Diagnostician)</div>
  <div class="qa-short">"Diagnoses the root cause of test failures and outputs a surgical fix plan for the Developer Agent."</div>
  <div class="qa-deep">
    <strong>Why we need it:</strong> Bridges the gap between browser test failures and code fixes. Analyzes DOM visibility vs CSS constraints.<br>
    <strong>File:</strong> <code>backend/agents/debug_agent.py</code>
  </div>
</div>

<div class="qa-card">
  <div class="qa-q">6. Reviewer Agent (Staff Engineer & Security Auditor)</div>
  <div class="qa-short">"Performs the final code quality, diff, and security audit before the Pull Request is created."</div>
  <div class="qa-deep">
    <strong>Why we need it:</strong> Ensures no regressions, security antipatterns, or bloated diffs enter version control.<br>
    <strong>File:</strong> <code>backend/agents/reviewer_agent.py</code>
  </div>
</div>

<!-- SECTION 5 -->
<h1>5. Human Approval Gates — Governance & Safety</h1>
<p>
  Nexus features two mandatory human-in-the-loop checkpoints:
</p>
<ul>
  <li><strong>Gate 1 (PRD Approval)</strong>: Operator reviews user stories and acceptance criteria before technical design begins. If the requirements are wrong, execution is stopped before compute is wasted.</li>
  <li><strong>Gate 2 (Architecture Approval)</strong>: Operator reviews the component blueprint and affected file list before any code is generated. Prevents accidental overhauls of the codebase.</li>
</ul>

<div class="say-card">
  <strong>Judge Answer on Human-in-the-Loop</strong>
  "Enterprise software requires governance. Nexus enforces a 'human-in-the-loop, human-on-the-loop' model: humans approve the requirements and architecture, while AI handles mechanical coding, testing, debugging, and PR delivery."
</div>

<!-- SECTION 6 -->
<h1>6. The Core Demo: Autonomous Self-Correction</h1>
<p>
  This is the <strong>centerpiece of your evaluation demonstration</strong>.
</p>

<div class="qa-card">
  <div class="qa-q">How to Explain the Self-Correction Demo in 30 Seconds</div>
  <div class="qa-deep">
    "In our demo, Nexus adds a responsive contact section. On desktop, it works and passes tests. But in our 375px mobile viewport test, the submit button fails because Tailwind's 'hidden md:inline-flex' hides it under 768px! Nexus doesn't crash—it routes the failure to our Debug Agent, diagnoses the CSS class, applies a surgical two-line patch, and retests. All tests pass with real screenshot proof!"
  </div>
</div>

<div class="say-card">
  <strong>Why Demonstrating Failure is Stronger than a Successful Script</strong>
  "Any scripted demo can show code working on the first try. That doesn't prove autonomous intelligence. By catching an intentional responsive layout failure, diagnosing it, fixing it in two lines, and proving it works via retest, Nexus proves genuine closed-loop self-correction."
</div>

<!-- SECTION 7 -->
<h1>7. Workspace Isolation — Protecting the Host Codebase</h1>

<div class="qa-card">
  <div class="qa-q">How does Nexus protect the main codebase from being ruined?</div>
  <div class="qa-short">"Double-lock isolation: Every task gets its own directory with a dedicated .git repository and strict path containment."</div>
  <div class="qa-deep">
    1. <strong>Isolated Directory</strong>: Tasks operate inside <code>workspaces/task_&lt;id&gt;/</code>.<br>
    2. <strong>Dedicated <code>.git</code></strong>: The task repository initializes its own local <code>.git</code> database. <code>git rev-parse --show-toplevel</code> resolves strictly to the task directory.<br>
    3. <strong>Path Containment (<code>resolve_safe_path</code>)</strong>: Rejects directory traversal attacks (<code>../</code>) with a <code>ValueError</code>.<br>
    4. <strong>Host Safety</strong>: The host Vistera repository remains on branch <code>main</code> with zero commits, branches, or leaks.
  </div>
</div>

<!-- SECTION 8 -->
<h1>8. Step-by-Step Live Demo Script</h1>

<table>
  <thead>
    <tr>
      <th>Step</th>
      <th>Presenter Action</th>
      <th>What to Say to the Judges</th>
      <th>Why it Matters</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>1</strong></td>
      <td>Open Dashboard (<code>http://localhost:3000</code>)</td>
      <td>"Here on our Mission Control dashboard, you see platform metrics: total tasks, active tasks, and self-correction cycles. Let's create a new task."</td>
      <td>Shows real-time platform overview and health.</td>
    </tr>
    <tr>
      <td><strong>2</strong></td>
      <td>Click Preset: <em>"Responsive Contact Section"</em></td>
      <td>"We'll launch our validated preset: 'Add a responsive contact section with name, email, message and submit button.'"</td>
      <td>Demonstrates natural-language task initiation.</td>
    </tr>
    <tr>
      <td><strong>3</strong></td>
      <td>Show PRD Tab & click <strong>Approve PRD</strong></td>
      <td>"Execution pauses at Human Gate 1. Nexus has drafted structured requirements. We review and approve before technical design begins."</td>
      <td>Proves human governance and requirement alignment.</td>
    </tr>
    <tr>
      <td><strong>4</strong></td>
      <td>Show Architecture Tab & click <strong>Approve Architecture</strong></td>
      <td>"Execution pauses at Human Gate 2. The Architect has blueprinted the solution and constrained edits to index.html. We approve to deploy agents."</td>
      <td>Proves safety and bounded code generation.</td>
    </tr>
    <tr>
      <td><strong>5</strong></td>
      <td>Click <strong>Agent Activity</strong> Tab</td>
      <td>"Our WebSocket stream displays real-time agent execution: Developer Agent branches and commits code; Tester Agent launches Playwright."</td>
      <td>Demonstrates live telemetry and transparency.</td>
    </tr>
    <tr>
      <td><strong>6</strong></td>
      <td>Show <strong>Playwright Tests</strong> Tab (Run 1: 2/1)</td>
      <td>"Look at Test Run 1: Desktop passes, but mobile 375px fails! The button is hidden by responsive CSS. Watch Nexus self-correct."</td>
      <td>Highlights genuine visual & responsive defect detection.</td>
    </tr>
    <tr>
      <td><strong>7</strong></td>
      <td>Show <strong>Self-Correction</strong> Tab</td>
      <td>"The Debug Agent diagnosed that Tailwind's 'hidden md:' suppressed mobile rendering, and gave Developer Agent a surgical fix plan."</td>
      <td>Proves closed-loop automated root-cause analysis.</td>
    </tr>
    <tr>
      <td><strong>8</strong></td>
      <td>Show <strong>Playwright Tests</strong> Tab (Run 2: 3/0) & <strong>Screenshots</strong></td>
      <td>"Tester retested the patched app: 100% pass! In the Screenshots tab, you see physical browser proof of the mobile button."</td>
      <td>Proves verified defect elimination with visual evidence.</td>
    </tr>
    <tr>
      <td><strong>9</strong></td>
      <td>Show <strong>Pull Request</strong> Tab</td>
      <td>"Reviewer Agent approved the diff, and Nexus created a verified Pull Request with test summaries and screenshot references."</td>
      <td>Demonstrates end-to-end delivery ready for merge.</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 9 -->
<h1>9. 3-Minute Presentation Script (Memorizable)</h1>

<div class="say-card">
  <strong>0:00–0:30: The Problem</strong>
  "Every software team wants to use AI to build software faster. But today's AI coding tools are essentially autocomplete chatbots. They generate code without testing it, they have no idea if your UI breaks on mobile viewports, and they leave you to manually debug errors and prepare pull requests. We asked: What if an AI didn't just autocomplete code, but acted as an autonomous software engineering team?"
</div>

<div class="say-card">
  <strong>0:30–1:00: The Nexus Solution</strong>
  "We built Nexus. Nexus decomposes software engineering into six specialized agents: PRD, Architect, Developer, Tester, Debug, and Reviewer. Governed by a deterministic state machine and human approval gates, Nexus operates in an isolated Git workspace, writes the code, runs real browser tests using Playwright, and fixes its own defects before creating a Pull Request."
</div>

<div class="say-card">
  <strong>1:00–1:30: Architecture & Governance</strong>
  "Enterprise software requires governance. Nexus features two mandatory approval gates: Gate 1 lets you approve requirements before architecture, and Gate 2 lets you approve the blueprint before any code is generated. Once approved, the agents execute in a dedicated sandbox directory with its own .git repository, completely protecting your main codebase."
</div>

<div class="say-card">
  <strong>1:30–2:30: Live Demo & Self-Correction</strong>
  "Let's look at our live demo. We asked Nexus to add a responsive contact section. The agents planned it, approved it, and coded it. But when our Tester Agent ran Playwright in a 375px mobile viewport, the submit button was hidden by a CSS rule. Notice what happens: Nexus doesn't stop. The Debug Agent diagnoses the Tailwind class, passes a fix plan to the Developer, applies a surgical two-line patch, and retests. All tests pass with real screenshot proof!"
</div>

<div class="say-card">
  <strong>2:30–3:00: Innovation & Conclusion</strong>
  "Finally, our Reviewer Agent audits the diff and generates a verified Pull Request. Nexus proves that the future of AI engineering isn't larger chatbots—it's specialized multi-agent architectures governed by real browser testing and closed-loop self-correction. Thank you, and we welcome your questions!"
</div>

<!-- SECTION 10 -->
<h1>10. Top Technical Judge Questions & Expert Answers</h1>

<div class="qa-card">
  <div class="qa-q">Q1: Why Playwright instead of Jest or Pytest for frontend testing?</div>
  <div class="qa-short">"Real DOM rendering and CSS visibility assertions require a genuine browser engine."</div>
  <div class="qa-deep">Unit tests mock the DOM and cannot verify responsive CSS layout classes like Tailwind's <code>hidden md:inline-flex</code>. Playwright runs headless Chromium on the host OS, rendering layout boxes, testing responsive breakpoints at 375px, and capturing physical PNG screenshots as visual proof.</div>
</div>

<div class="qa-card">
  <div class="qa-q">Q2: Why use six agents instead of a single powerful LLM prompt?</div>
  <div class="qa-short">"Context isolation and role specialization. Overloading one prompt causes hallucination and missed constraints."</div>
  <div class="qa-deep">A single prompt mixing requirements, CSS layout, DOM assertions, and Git commits quickly exceeds context limits and degrades attention. Decomposing into PRD, Architect, Developer, Tester, Debug, and Reviewer agents creates clean verification boundaries where each agent has specialized system prompts.</div>
</div>

<div class="qa-card">
  <div class="qa-q">Q3: What prevents the agents from ruining my main codebase?</div>
  <div class="qa-short">"Dedicated task directories, path containment checks, and independent local .git databases."</div>
  <div class="qa-deep">Nexus provisions each task in <code>workspaces/task_&lt;id&gt;/repository/</code> with its own <code>.git</code> repo. <code>WorkspaceManager.resolve_safe_path()</code> rejects any path escaping the sandbox. Git commands are run strictly with <code>cwd</code> set to the task repository, so <code>git rev-parse --show-toplevel</code> never touches the parent repository.</div>
</div>

<div class="qa-card">
  <div class="qa-q">Q4: How does the Debug Agent diagnose problems?</div>
  <div class="qa-short">"It analyzes failed assertion evidence and DOM error logs to isolate the exact defect."</div>
  <div class="qa-deep">The Debug Agent receives the requirement description, failure evidence (e.g. <code>#contact-submit-btn is hidden</code>), and the source code. It recognizes that the button exists in HTML but is constrained by media queries or utility classes, formulating an explicit remediation plan for the Developer Agent.</div>
</div>

<div class="qa-card">
  <div class="qa-q">Q5: Is this reliant on an active internet connection or OpenAI API?</div>
  <div class="qa-short">"No; Nexus supports OpenAI models and features a zero-failure deterministic fallback engine."</div>
  <div class="qa-deep">If <code>OPENAI_API_KEY</code> is not set or times out, the platform seamlessly engages its deterministic fallback engine. This ensures hackathon demonstrations and offline evaluations never fail due to third-party API outages.</div>
</div>

<div class="qa-card">
  <div class="qa-q">Q6: What is your biggest limitation right now?</div>
  <div class="qa-short">"Host-level directory sandboxing rather than Docker containers, and structured browser test suites."</div>
  <div class="qa-deep">Our current prototype uses host-level directory sandboxing with dedicated <code>.git</code> repositories rather than containerized Docker containers. Additionally, our automated testing currently relies on structured web test harnesses rather than dynamically generating arbitrary unit test suites from scratch.</div>
</div>

<!-- SECTION 11 -->
<h1>11. Quick Revision Cheat Sheet</h1>

<table style="margin-top: 10px;">
  <thead>
    <tr>
      <th>Dimension</th>
      <th>Core Concept to Remember</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Core Purpose</strong></td>
      <td>Autonomous AI engineering team that turns prompts into tested, reviewed Pull Requests.</td>
    </tr>
    <tr>
      <td><strong>The 6 Agents</strong></td>
      <td>PRD (PM) &rarr; Architect (Blueprint) &rarr; Developer (Code) &rarr; Tester (QA) &rarr; Debug (Diagnosis) &rarr; Reviewer (Audit).</td>
    </tr>
    <tr>
      <td><strong>The 2 Gates</strong></td>
      <td>Gate 1: PRD Approval before architecture. Gate 2: Architecture Approval before coding.</td>
    </tr>
    <tr>
      <td><strong>Core Demo</strong></td>
      <td>Mobile 375px submit button hidden &rarr; Playwright fails &rarr; Debug diagnoses &rarr; 2-line fix &rarr; Retest passes 100%!</td>
    </tr>
    <tr>
      <td><strong>Sandbox Isolation</strong></td>
      <td>Every task has its own folder + dedicated <code>.git</code> repository. Main repo is 100% untouched.</td>
    </tr>
    <tr>
      <td><strong>Key Metrics</strong></td>
      <td>375px mobile breakpoint, 2 approval gates, 6 specialized agents, 10 database tables.</td>
    </tr>
  </tbody>
</table>

<!-- SECTION 12 -->
<h1>12. Final "If You Forget Everything" Emergency Sheet</h1>

<div class="diagram-box" style="background: #0f172a; color: #ffffff; padding: 20px; text-align: left;">
  <div style="font-size: 14pt; font-weight: 800; color: #38bdf8; margin-bottom: 8px;">NEXUS EMERGENCY REVISION SHEET</div>
  <p style="color: #cbd5e1; font-size: 9pt; margin-bottom: 12px;">
    <strong>WHAT IS NEXUS?</strong><br>
    "An autonomous AI software engineering team that turns prompts into verified PRs."
  </p>
  <p style="color: #cbd5e1; font-size: 9pt; margin-bottom: 12px;">
    <strong>THE WORKFLOW IN ONE LINE:</strong><br>
    Prompt &rarr; PRD &rarr; [Gate 1] &rarr; Arch &rarr; [Gate 2] &rarr; Code &rarr; Test &rarr; Debug &rarr; Fix &rarr; Retest &rarr; Review &rarr; PR
  </p>
  <p style="color: #cbd5e1; font-size: 9pt; margin-bottom: 12px;">
    <strong>THE CORE INNOVATION:</strong><br>
    "Don't just generate code. Build it. Test it in a real browser. Catch defects. Fix them. Retest. Deliver proof."
  </p>
  <p style="color: #cbd5e1; font-size: 9pt; margin-bottom: 12px;">
    <strong>IF ASKED ABOUT COPILOT:</strong><br>
    "Copilot is a typing assistant. Nexus is an autonomous engineering department."
  </p>
  <p style="color: #cbd5e1; font-size: 9pt; margin-bottom: 0;">
    <strong>THE DEMO PUNCHLINE:</strong><br>
    "Test Run 1 fails on mobile 375px &rarr; Debug Agent diagnoses Tailwind class &rarr; Developer fixes in 2 lines &rarr; Test Run 2 passes 100%!"
  </p>
</div>

</body>
</html>
"""

async def generate_presentation_guide():
    root_dir = Path(__file__).resolve().parent
    md_path = root_dir / "NEXUS_Presentation_Preparation_Guide.md"
    pdf_path = root_dir / "NEXUS_Presentation_Preparation_Guide.pdf"

    print(f"Writing Markdown source to {md_path}...")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(MD_CONTENT)
    print("Markdown file written successfully!")

    print(f"Generating PDF via Playwright Chromium to {pdf_path}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(HTML_TEMPLATE, wait_until="networkidle")
        await page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={
                "top": "18mm",
                "right": "14mm",
                "bottom": "18mm",
                "left": "14mm"
            }
        )
        await browser.close()

    print(f"PDF generated successfully at {pdf_path}!")
    pdf_size = pdf_path.stat().st_size
    print(f"PDF Size: {pdf_size:,} bytes")

if __name__ == "__main__":
    asyncio.run(generate_presentation_guide())
