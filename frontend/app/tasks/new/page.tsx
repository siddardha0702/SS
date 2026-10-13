'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createTask } from '../../../lib/api';
import {
  ArrowLeft,
  Sparkles,
  FolderGit2,
  Loader2,
  Play,
  Cpu,
  ShieldCheck,
  Terminal,
  Layers,
  GitPullRequest,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import Link from 'next/link';

export default function NewTaskPage() {
  const router = useRouter();
  const [repository, setRepository] = useState('sample_repo');
  const [featureRequest, setFeatureRequest] = useState(
    'Add a responsive contact section with name, email, message and submit button.'
  );
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const presets = [
    {
      title: 'Responsive Contact Section',
      repo: 'sample_repo',
      prompt: 'Add a responsive contact section with name, email, message and submit button.',
      highlight: true,
      tag: 'Round 3/4 Verified Scenario',
    },
    {
      title: 'Wishlist Button (Triggers Self-Correction)',
      repo: 'sample_repo',
      prompt: 'Add a wishlist button to every product card with live counter badge and responsive mobile layout.',
      highlight: true,
      tag: 'Playwright Bug & Auto-Fix',
    },
    {
      title: 'Search & Category Filter',
      repo: 'sample_repo',
      prompt: 'Add instant live search filtering to products and a category tag selector.',
      highlight: false,
      tag: 'Feature Addition',
    },
    {
      title: 'Dark / Light Theme Toggle',
      repo: 'sample_repo',
      prompt: 'Add a theme switch in the top navigation bar to toggle light and dark modes with local storage persistence.',
      highlight: false,
      tag: 'UI Polish',
    },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repository.trim() || !featureRequest.trim()) {
      setErrorMsg('Please specify both a target repository and feature request description.');
      return;
    }

    setLoading(true);
    setErrorMsg(null);
    try {
      const task = await createTask(repository.trim(), featureRequest.trim());
      router.push(`/tasks/${task.id}`);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to initialize task. Ensure backend server is reachable at localhost:8000.');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back button */}
      <Link
        href="/"
        className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-400 hover:text-white transition"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Dashboard</span>
      </Link>

      <div className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-semibold text-blue-400 mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Autonomous Pipeline Orchestrator</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Launch Autonomous Engineering Task
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Nexus provisions an isolated sandbox workspace, deploys 6 specialized AI agents, and guides execution through verification gates.
          </p>
        </div>

        {errorMsg && (
          <div className="p-3.5 rounded-xl bg-red-950/40 border border-red-500/30 text-xs text-red-300 flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Evaluation Presets */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs font-bold text-slate-300 uppercase tracking-wider block">
              Evaluator Demo Scenarios
            </label>
            <span className="text-[11px] text-slate-500">Click to load pre-tested feature prompts</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {presets.map((p, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setRepository(p.repo);
                  setFeatureRequest(p.prompt);
                }}
                className={`p-3.5 rounded-2xl border text-left transition-all flex flex-col justify-between ${
                  featureRequest === p.prompt
                    ? 'bg-blue-950/40 border-blue-500/80 ring-1 ring-blue-500'
                    : 'bg-slate-900/40 border-slate-800/80 hover:border-slate-700'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-white">{p.title}</span>
                    <span
                      className={`text-[10px] px-2 py-0.2 rounded-full font-semibold border ${
                        p.highlight
                          ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                          : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}
                    >
                      {p.tag}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-relaxed line-clamp-2">{p.prompt}</p>
                </div>
                <div className="mt-2 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-500">
                  <span className="font-mono">repo: {p.repo}</span>
                  <span className="text-blue-400 font-semibold flex items-center space-x-1">
                    <span>Select Preset</span>
                    <Play className="w-2.5 h-2.5 fill-blue-400" />
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Task Form */}
        <form onSubmit={handleSubmit} className="space-y-4 pt-3 border-t border-slate-800/80">
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-bold text-slate-300 uppercase tracking-wider block">
                Target Repository
              </label>
              <div className="flex items-center space-x-2 text-[11px]">
                <button
                  type="button"
                  onClick={() => setRepository('sample_repo')}
                  className="text-blue-400 hover:underline"
                >
                  Use sample_repo
                </button>
                <span className="text-slate-600">&bull;</span>
                <button
                  type="button"
                  onClick={() => setRepository('https://github.com/siddardha0702/Nexus2')}
                  className="text-blue-400 hover:underline"
                >
                  Use siddardha0702/Nexus2
                </button>
              </div>
            </div>

            <div className="relative">
              <FolderGit2 className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
              <input
                type="text"
                value={repository}
                onChange={(e) => setRepository(e.target.value)}
                placeholder="sample_repo or https://github.com/user/repo"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-blue-500 font-mono"
                required
              />
            </div>
            <p className="text-[11px] text-slate-500 mt-1">
              Supports local sample repositories and remote GitHub repositories. A temporary isolated branch is created automatically.
            </p>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              Feature Request / Engineering Objective
            </label>
            <textarea
              value={featureRequest}
              onChange={(e) => setFeatureRequest(e.target.value)}
              placeholder="Describe the feature requirement or bug fix in natural language..."
              rows={4}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-blue-500 leading-relaxed"
              required
            />
            <p className="text-[11px] text-slate-500 mt-1">
              Be descriptive. The PRD Agent will formalize this into strict acceptance criteria, Definition of Done, and edge cases.
            </p>
          </div>

          {/* Sequential Lifecycle Preview */}
          <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-2.5">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
              What Happens Next (Autonomous Sequence)
            </span>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
              <div className="p-2 rounded-lg bg-slate-900 border border-slate-800/80">
                <div className="font-semibold text-purple-400 text-[11px]">1. PRD Agent</div>
                <div className="text-[10px] text-slate-400">Generates formal spec &rarr; Gate 1 Approval</div>
              </div>
              <div className="p-2 rounded-lg bg-slate-900 border border-slate-800/80">
                <div className="font-semibold text-indigo-400 text-[11px]">2. Architect</div>
                <div className="text-[10px] text-slate-400">Plans target files &rarr; Gate 2 Approval</div>
              </div>
              <div className="p-2 rounded-lg bg-slate-900 border border-slate-800/80">
                <div className="font-semibold text-blue-400 text-[11px]">3. Dev & Tests</div>
                <div className="text-[10px] text-slate-400">Codes in sandbox & executes Playwright</div>
              </div>
              <div className="p-2 rounded-lg bg-slate-900 border border-slate-800/80">
                <div className="font-semibold text-emerald-400 text-[11px]">4. Review & PR</div>
                <div className="text-[10px] text-slate-400">Self-corrects if needed & creates PR</div>
              </div>
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-blue-600/30 transition flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Provisioning Workspace & Spawning PRD Agent...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Initialize Nexus Team & Begin PRD Generation</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
