'use client';

import React from 'react';
import Link from 'next/link';
import {
  HelpCircle,
  Cpu,
  ShieldCheck,
  Terminal,
  Layers,
  GitPullRequest,
  CheckCircle2,
  AlertTriangle,
  Bug,
  FileText,
  Compass,
  Code2,
  ExternalLink,
  Sparkles,
  ArrowRight,
} from 'lucide-react';

export default function HelpPage() {
  const steps = [
    {
      num: '01',
      agent: 'User Request',
      title: 'Prompt Ingestion',
      desc: 'The engineer inputs a high-level natural language prompt and target Git repository.',
      tag: 'Input',
      tagColor: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
    },
    {
      num: '02',
      agent: 'PRD Agent',
      title: 'Requirements Synthesis',
      desc: 'Synthesizes formal PRD Document with acceptance criteria, Definition of Done, and edge cases.',
      tag: 'Agent 1',
      tagColor: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
    },
    {
      num: '03',
      agent: 'Human In The Loop',
      title: 'Human Gate 1 (PRD)',
      desc: 'Execution pauses deterministically until the human engineer approves or requests PRD revisions.',
      tag: 'Gate 1',
      tagColor: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
    },
    {
      num: '04',
      agent: 'Architect Agent',
      title: 'System Blueprint',
      desc: 'Audits AST and codebase files; designs technical blueprint detailing target files and API contracts.',
      tag: 'Agent 2',
      tagColor: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20',
    },
    {
      num: '05',
      agent: 'Human In The Loop',
      title: 'Human Gate 2 (Architecture)',
      desc: 'Execution pauses deterministically until the human engineer approves technical architecture.',
      tag: 'Gate 2',
      tagColor: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
    },
    {
      num: '06',
      agent: 'Developer Agent',
      title: 'Isolated Implementation',
      desc: 'Provisions temporary Git workspace sandbox; applies surgical code modifications with AST checks.',
      tag: 'Agent 3',
      tagColor: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
    },
    {
      num: '07',
      agent: 'Tester Agent',
      title: 'Playwright Verification',
      desc: 'Launches headless Playwright Chromium, executes multi-viewport tests, and captures screenshots.',
      tag: 'Agent 4',
      tagColor: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    },
    {
      num: '08',
      agent: 'Debug / Fix Agent',
      title: 'Self-Correction Loop',
      desc: 'If any assertion fails, Debug Agent determines root cause and instructs Developer to fix and re-test.',
      tag: 'Agent 5',
      tagColor: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
    },
    {
      num: '09',
      agent: 'Reviewer Agent',
      title: 'Diff & Security Audit',
      desc: 'Audits complete Git diff against PRD requirements, verifies passing tests, and creates GitHub PR.',
      tag: 'Agent 6',
      tagColor: 'text-teal-400 bg-teal-500/10 border-teal-500/20',
    },
    {
      num: '10',
      agent: 'GitHub / Git Remote',
      title: 'Verified Pull Request',
      desc: 'Pushes isolated branch and opens a production-grade verified Pull Request.',
      tag: 'Output',
      tagColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    },
  ];

  const faqs = [
    {
      q: 'How does Nexus differ from single-prompt AI code generators?',
      a: 'Single-prompt assistants hallucinate edits and have no verification loop. Nexus enforces a deterministic state machine with 6 specialized agents, 2 human approval gates, real headless browser testing, and autonomous self-correction before any Pull Request is produced.',
    },
    {
      q: 'What happens when Playwright browser tests fail?',
      a: 'Nexus does not crash or give up. The Tester Agent passes DOM failure logs to the Debug Agent, which diagnoses the root cause (e.g. CSS breakpoint hidden on mobile 375px), generates a surgical fix plan, and instructs the Developer Agent to implement the fix and re-test.',
    },
    {
      q: 'Can a human reject or edit a PRD or Architecture document?',
      a: 'Yes. At Gate 1 (PRD) and Gate 2 (Architecture), execution halts completely. The user can either click Approve to proceed, or click Reject and provide specific revision instructions.',
    },
    {
      q: 'How is code sandbox safety maintained?',
      a: 'The WorkspaceManager provisions an isolated directory for every task. Path traversal attempts are blocked via strict path validation, and changes are committed only to isolated task branches.',
    },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-10">
      {/* Hero Header */}
      <div>
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-semibold text-blue-400 mb-3">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Architecture & System Documentation</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
          How Nexus Works: The Autonomous Engineering Pipeline
        </h1>
        <p className="text-sm text-slate-300 mt-2 max-w-3xl leading-relaxed">
          Nexus solves the fundamental limitations of AI code generation by decoupling engineering into specialized roles, enforcing human approval checkpoints, and closing the feedback loop with headless browser testing.
        </p>
      </div>

      {/* Visual Execution Flow */}
      <div className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-blue-400" />
            <span>Deterministic Ten-Stage Execution Flow</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Strictly ordered state transitions guaranteed by the backend orchestrator
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {steps.map((st, idx) => (
            <div
              key={idx}
              className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80 flex items-start space-x-3.5 hover:border-slate-700 transition"
            >
              <div className="w-9 h-9 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-center text-xs font-mono font-bold text-slate-400 flex-shrink-0">
                {st.num}
              </div>
              <div className="space-y-1 flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">{st.title}</span>
                  <span className={`text-[10px] font-bold px-2 py-0.2 rounded-full border ${st.tagColor}`}>
                    {st.tag}
                  </span>
                </div>
                <div className="text-[11px] font-semibold text-blue-400">{st.agent}</div>
                <p className="text-xs text-slate-400 leading-relaxed">{st.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Architectural Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div id="human-gates" className="p-6 rounded-3xl bg-[#0b1120] border border-slate-800 shadow-xl space-y-3">
          <div className="w-10 h-10 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white">Two Human Approval Gates</h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            AI agents should never write code without architectural consensus. Gate 1 gives you authority over PRD scope. Gate 2 gives you authority over technical implementation plans.
          </p>
        </div>

        <div id="self-correction" className="p-6 rounded-3xl bg-[#0b1120] border border-slate-800 shadow-xl space-y-3">
          <div className="w-10 h-10 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-center">
            <Bug className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white">Autonomous Self-Correction</h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            Headless Playwright tests detect responsive layout bugs (e.g. mobile 375px). The Debug Agent analyzes the failure stack trace, formulates a targeted fix, and developer re-tests automatically.
          </p>
        </div>

        <div id="security" className="p-6 rounded-3xl bg-[#0b1120] border border-slate-800 shadow-xl space-y-3">
          <div className="w-10 h-10 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center">
            <Terminal className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white">Workspace Sandboxing</h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            All code modifications occur within temporary isolated task directories. Path traversal protection prevents unauthorized filesystem access, and output is cleanly packaged as a verified Pull Request.
          </p>
        </div>
      </div>

      {/* Judge & Evaluator FAQ */}
      <div className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl space-y-6">
        <div>
          <h2 className="text-base font-bold text-white flex items-center space-x-2">
            <HelpCircle className="w-4 h-4 text-blue-400" />
            <span>Frequently Asked Questions & Evaluation Reference</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Key questions regarding Nexus autonomy, safety, and evaluation scenarios
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {faqs.map((faq, idx) => (
            <div key={idx} className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
              <h4 className="text-xs font-bold text-white">{faq.q}</h4>
              <p className="text-xs text-slate-400 leading-relaxed">{faq.a}</p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Box */}
      <div className="p-8 rounded-3xl bg-gradient-to-r from-blue-950/40 via-indigo-950/40 to-slate-900 border border-blue-500/30 text-center space-y-4">
        <h3 className="text-xl font-bold text-white">Experience Nexus in Action</h3>
        <p className="text-xs text-slate-300 max-w-xl mx-auto">
          Launch our preconfigured scenario to observe PRD formulation, approval gates, Playwright mobile test failure, and autonomous self-correction.
        </p>
        <Link
          href="/tasks/new"
          className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold shadow-lg shadow-blue-600/30 transition"
        >
          <span>Launch Evaluation Task</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
