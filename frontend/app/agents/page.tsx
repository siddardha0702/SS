'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { fetchTasks } from '../../lib/api';
import { Task } from '../../types';
import {
  Cpu,
  FileText,
  Compass,
  Code2,
  CheckCircle2,
  Bug,
  GitPullRequest,
  ShieldCheck,
  Terminal,
  Layers,
  ArrowRight,
  Sparkles,
  Play,
} from 'lucide-react';

export default function AgentsPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTasks()
      .then((data) => setTasks(data))
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  const completedCount = tasks.filter((t) => t.status === 'COMPLETED').length;
  const selfCorrectionsCount = tasks.reduce((sum, t) => sum + (t.retry_count || 0), 0);

  const agents = [
    {
      id: 'prd_agent',
      number: '1',
      name: 'PRD Agent',
      role: 'Product Requirements & Acceptance Criteria',
      badgeColor: 'border-purple-500/30 bg-purple-500/10 text-purple-400',
      icon: FileText,
      gate: 'Human Gate 1 (PRD Approval)',
      summary:
        'Analyzes high-level natural language feature requests and synthesizes a comprehensive Product Requirements Document (PRD) detailing business goals, strict acceptance criteria, Definition of Done, and edge cases.',
      tools: ['LLM Specification Engine', 'Schema Validator', 'Scope Boundary Enforcement'],
      inputs: 'User feature prompt + Target repository path',
      outputs: 'Formal PRD Document with acceptance criteria array',
      safety: 'Requires explicit human sign-off before downstream agents proceed.',
    },
    {
      id: 'architect_agent',
      number: '2',
      name: 'Architect Agent',
      role: 'System Blueprint & File-Level Plan',
      badgeColor: 'border-indigo-500/30 bg-indigo-500/10 text-indigo-400',
      icon: Compass,
      gate: 'Human Gate 2 (Architecture Approval)',
      summary:
        'Inspects the codebase structure, audits files, and designs a surgical technical blueprint detailing files to modify, files to create, dependencies, and step-by-step implementation sequencing.',
      tools: ['AST Parser', 'Repository File Scanner', 'Dependency Graph Analyzer'],
      inputs: 'Approved PRD Document + Repository context',
      outputs: 'Architecture Document + Step-by-step modification blueprint',
      safety: 'Subject to Human Gate 2 approval prior to executing code modifications.',
    },
    {
      id: 'developer_agent',
      number: '3',
      name: 'Developer Agent',
      role: 'Isolated Sandbox Code Implementation',
      badgeColor: 'border-blue-500/30 bg-blue-500/10 text-blue-400',
      icon: Code2,
      gate: null,
      summary:
        'Provisions an isolated Git workspace sandbox and implements the code changes specified by the Architecture blueprint. Ensures strict adherence to path traversal security and commits atomic changes.',
      tools: ['Git Workspace Sandbox', 'Path Traversal Guard', 'Syntax AST Linter'],
      inputs: 'Approved Architecture Document + Workspace sandbox path',
      outputs: 'Source code modifications + Git branch commits',
      safety: 'Sandboxed in temporary workspace; never writes directly to production repository.',
    },
    {
      id: 'tester_agent',
      number: '4',
      name: 'Tester Agent',
      role: 'Playwright Browser Verification',
      badgeColor: 'border-amber-500/30 bg-amber-500/10 text-amber-400',
      icon: CheckCircle2,
      gate: null,
      summary:
        'Boots the application web server, launches headless Playwright Chromium, and runs multi-viewport browser tests (Desktop & Mobile 375px) to verify DOM elements and capture visual regression screenshots.',
      tools: ['Playwright Headless Chromium', 'DOM Assertion Engine', 'Screenshot Capture'],
      inputs: 'Modified codebase in sandbox + PRD acceptance criteria',
      outputs: 'TestRun entity with assertions + Full-page visual screenshots',
      safety: 'Headless browser execution validates actual runtime behavior.',
    },
    {
      id: 'debug_agent',
      number: '5',
      name: 'Debug / Fix Agent',
      role: 'Failure Diagnosis & Self-Correction',
      badgeColor: 'border-rose-500/30 bg-rose-500/10 text-rose-400',
      icon: Bug,
      gate: null,
      summary:
        'Automatically triggered whenever Playwright tests encounter failures. Analyzes Playwright error logs, pinpoints root causes (e.g. mobile CSS breakpoints), formulates a surgical fix plan, and guides the Developer Agent.',
      tools: ['Playwright Log Analyzer', 'Root Cause Engine', 'Surgical Fix Generator'],
      inputs: 'Failed TestRun assertions + Browser console logs',
      outputs: 'DebugReport entity + Corrected code instructions',
      safety: 'Capped retry loop (max 3 cycles) prevents infinite execution loops.',
    },
    {
      id: 'reviewer_agent',
      number: '6',
      name: 'Reviewer Agent',
      role: 'Diff Audit & GitHub PR Creation',
      badgeColor: 'border-teal-500/30 bg-teal-500/10 text-teal-400',
      icon: GitPullRequest,
      gate: null,
      summary:
        'Audits the complete Git diff against PRD specifications, confirms test pass status, generates structured release notes, and pushes the branch to remote to create a verified GitHub Pull Request.',
      tools: ['Git Diff Auditor', 'Security Guardrail Check', 'GitHub REST API Client'],
      inputs: 'Passing test run + Full git diff + Workspace context',
      outputs: 'ReviewResult entity + Official GitHub Pull Request',
      safety: 'Only produces PR after 100% of Playwright tests pass.',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-semibold text-blue-400 mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Autonomous AI Hierarchy</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            The Six Specialized AI Engineering Agents
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-3xl">
            Nexus divides software engineering into specialized, autonomous agent roles coordinated by a deterministic state machine.
          </p>
        </div>

        <Link
          href="/tasks/new"
          className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/30 transition flex items-center space-x-1.5 self-start sm:self-auto"
        >
          <Play className="w-3.5 h-3.5 fill-white" />
          <span>Launch Pipeline</span>
        </Link>
      </div>

      {/* Aggregate Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#0b1120] border border-slate-800/80 rounded-2xl p-4 shadow-lg">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Agents Defined</div>
          <div className="text-2xl font-bold text-white font-mono mt-1">6 Active</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Strict state machine</div>
        </div>

        <div className="bg-[#0b1120] border border-slate-800/80 rounded-2xl p-4 shadow-lg">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Human Gates</div>
          <div className="text-2xl font-bold text-amber-400 font-mono mt-1">2 Gates</div>
          <div className="text-[11px] text-slate-500 mt-0.5">PRD & Architecture</div>
        </div>

        <div className="bg-[#0b1120] border border-slate-800/80 rounded-2xl p-4 shadow-lg">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Total PRs Verified</div>
          <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">{completedCount}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Verified by Reviewer</div>
        </div>

        <div className="bg-[#0b1120] border border-slate-800/80 rounded-2xl p-4 shadow-lg">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Self-Corrections</div>
          <div className="text-2xl font-bold text-rose-400 font-mono mt-1">{selfCorrectionsCount}</div>
          <div className="text-[11px] text-slate-500 mt-0.5">Playwright loop fixes</div>
        </div>
      </div>

      {/* Agent Detail Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {agents.map((ag) => {
          const Icon = ag.icon;
          return (
            <div
              key={ag.id}
              className="bg-[#0b1120] border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col justify-between space-y-4 hover:border-slate-700 transition"
            >
              <div className="space-y-3">
                {/* Agent Header */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2.5">
                    <div className="w-8 h-8 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-white">
                      <Icon className="w-4 h-4 text-blue-400" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-white">{ag.name}</h3>
                      <p className="text-[11px] text-slate-400">{ag.role}</p>
                    </div>
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${ag.badgeColor}`}>
                    #{ag.number}
                  </span>
                </div>

                {/* Summary */}
                <p className="text-xs text-slate-300 leading-relaxed">{ag.summary}</p>

                {/* Gate notice if applicable */}
                {ag.gate && (
                  <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-300 flex items-center space-x-1.5 font-medium">
                    <ShieldCheck className="w-3.5 h-3.5 flex-shrink-0" />
                    <span>Enforces {ag.gate}</span>
                  </div>
                )}

                {/* Key Tools */}
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1.5">
                    Integrated Tooling
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {ag.tools.map((t, idx) => (
                      <span
                        key={idx}
                        className="text-[10px] bg-slate-900 text-slate-300 border border-slate-800 px-2 py-0.5 rounded font-mono"
                      >
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Safety Footprint */}
              <div className="pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
                <span className="font-semibold text-slate-300">Safety Guarantee: </span>
                {ag.safety}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
