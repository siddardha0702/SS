'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { fetchTasks, createTask, fetchSampleRepo } from '../lib/api';
import { Task } from '../types';
import {
  Layers,
  PlusCircle,
  Play,
  GitPullRequest,
  CheckCircle2,
  Clock,
  ArrowRight,
  ShieldCheck,
  Cpu,
  Bug,
  Sparkles,
  ExternalLink,
  Search,
  AlertTriangle,
  FolderGit2,
  Activity,
  Radio,
  FileText,
  Compass,
  Code2,
  Terminal,
} from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [demoLaunching, setDemoLaunching] = useState(false);
  const [filter, setFilter] = useState<'ALL' | 'ACTIVE' | 'PENDING' | 'COMPLETED' | 'FAILED'>('ALL');
  const [search, setSearch] = useState('');

  const loadTasks = async () => {
    try {
      const data = await fetchTasks();
      setTasks(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
    const interval = setInterval(loadTasks, 4000);
    return () => clearInterval(interval);
  }, []);

  const launchDemo = async () => {
    setDemoLaunching(true);
    try {
      const sample = await fetchSampleRepo();
      const repoUrl = sample?.path || 'sample_repo';
      const feature = 'Add a wishlist button to every product card with live counter badge and responsive mobile layout.';
      const created = await createTask(repoUrl, feature);
      router.push(`/tasks/${created.id}`);
    } catch (err) {
      alert('Error launching demo: ' + err);
      setDemoLaunching(false);
    }
  };

  // Real backend calculations
  const completedCount = tasks.filter((t) => t.status === 'COMPLETED').length;
  const activeCount = tasks.filter((t) => !['COMPLETED', 'CANCELLED'].includes(t.status) && !t.status.includes('FAILED')).length;
  const failedCount = tasks.filter((t) => t.status.includes('FAILED') || t.status === 'CANCELLED').length;
  const pendingCount = tasks.filter((t) => t.status.includes('PENDING_APPROVAL')).length;
  const retriesCount = tasks.reduce((acc, t) => acc + (t.retry_count || 0), 0);

  // Latest verified PR
  const latestCompletedTask = tasks.find((t) => t.status === 'COMPLETED' && t.github_pr_url);

  // Filtered task list
  const filteredTasks = tasks.filter((t) => {
    const matchesSearch =
      t.feature_request.toLowerCase().includes(search.toLowerCase()) ||
      t.repository.toLowerCase().includes(search.toLowerCase()) ||
      t.id.toLowerCase().includes(search.toLowerCase());

    if (!matchesSearch) return false;

    if (filter === 'ACTIVE') {
      return !['COMPLETED', 'CANCELLED'].includes(t.status) && !t.status.includes('FAILED');
    }
    if (filter === 'PENDING') {
      return t.status.includes('PENDING_APPROVAL');
    }
    if (filter === 'COMPLETED') {
      return t.status === 'COMPLETED';
    }
    if (filter === 'FAILED') {
      return t.status.includes('FAILED') || t.status === 'CANCELLED';
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Top Production Metrics Row (Responsive 5-card grid) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5 sm:gap-4">
        <div className="bg-[#0b1120] border border-slate-800/80 rounded-2xl p-4 shadow-lg hover:border-slate-700/80 transition">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Total Tasks</span>
            <Layers className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">{tasks.length}</div>
          <div className="text-[10px] text-slate-500 mt-0.5">Initialized workflows</div>
        </div>

        <div className="bg-[#0b1120] border border-slate-800/80 rounded-2xl p-4 shadow-lg hover:border-slate-700/80 transition">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Active Pipelines</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400 font-mono">{activeCount}</div>
          <div className="text-[10px] text-slate-500 mt-0.5">In-flight stages</div>
        </div>

        <div className="bg-[#0b1120] border border-slate-800/80 rounded-2xl p-4 shadow-lg hover:border-slate-700/80 transition">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Completed PRs</span>
            <GitPullRequest className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400 font-mono">{completedCount}</div>
          <div className="text-[10px] text-slate-500 mt-0.5">Verified & merged</div>
        </div>

        <div className="bg-[#0b1120] border border-slate-800/80 rounded-2xl p-4 shadow-lg hover:border-slate-700/80 transition">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Self-Corrections</span>
            <Bug className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold text-rose-400 font-mono">{retriesCount}</div>
          <div className="text-[10px] text-slate-500 mt-0.5">Auto bug fix cycles</div>
        </div>

        <div className="bg-[#0b1120] border border-slate-800/80 rounded-2xl p-4 shadow-lg hover:border-slate-700/80 transition col-span-2 sm:col-span-1">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Failed / Cancelled</span>
            <AlertTriangle className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-slate-300 font-mono">{failedCount}</div>
          <div className="text-[10px] text-slate-500 mt-0.5">Stopped executions</div>
        </div>
      </div>

      {/* Main Dual-Column Desktop Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left / Main Section (8 cols on desktop) */}
        <div className="lg:col-span-8 space-y-6">
          {/* Hero SaaS Header & Controls Banner */}
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-950/40 via-slate-900 to-indigo-950/30 border border-slate-800 p-6 shadow-2xl">
            <div className="relative z-10">
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-semibold text-blue-400 mb-3">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Autonomous AI Software Engineering Team</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight leading-tight">
                Autonomous Engineering Control Console
              </h1>
              <p className="text-xs sm:text-sm text-slate-300 mt-2 leading-relaxed max-w-2xl">
                From natural language prompts to formal PRD generation, architectural blueprinting, isolated workspace coding,
                headless Playwright browser testing, autonomous self-correction, and verified GitHub Pull Requests.
              </p>

              <div className="flex flex-wrap items-center gap-3 mt-5">
                <button
                  onClick={launchDemo}
                  disabled={demoLaunching}
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-blue-600/30 transition flex items-center space-x-2 disabled:opacity-50"
                >
                  <Play className="w-4 h-4 fill-white" />
                  <span>{demoLaunching ? 'Provisioning Workspace & Agents...' : 'Launch Instant Evaluation Demo'}</span>
                </button>

                <Link
                  href="/tasks/new"
                  className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold border border-slate-700 transition flex items-center space-x-2"
                >
                  <PlusCircle className="w-4 h-4 text-blue-400" />
                  <span>Create Custom Task</span>
                </Link>

                <Link
                  href="/help"
                  className="px-3.5 py-2.5 rounded-xl bg-slate-900/60 hover:bg-slate-800 text-slate-300 text-xs font-medium border border-slate-800 transition flex items-center space-x-1.5"
                >
                  <span>System Guide</span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
                </Link>
              </div>
            </div>
          </div>

          {/* Latest Verified Pull Request Banner (If Available) */}
          {latestCompletedTask && (
            <div className="bg-gradient-to-r from-emerald-950/30 via-slate-900 to-[#0b1120] border border-emerald-500/30 rounded-2xl p-5 shadow-xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold uppercase tracking-wider flex items-center space-x-1">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>Latest Verified Pull Request</span>
                    </span>
                    <span className="text-xs text-slate-400 font-mono">{latestCompletedTask.branch_name}</span>
                  </div>
                  <h3 className="text-sm font-bold text-white">
                    {latestCompletedTask.feature_request}
                  </h3>
                  <p className="text-xs text-slate-400 break-words">
                    Playwright browser tests passed &bull; Reviewer Agent approved &bull; Repository:{' '}
                    <span className="font-mono text-slate-300 break-all">{latestCompletedTask.repository}</span>
                  </p>
                </div>

                <div className="flex items-center space-x-2.5 flex-shrink-0">
                  <Link
                    href={`/tasks/${latestCompletedTask.id}`}
                    className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold border border-slate-700 transition flex items-center space-x-1.5"
                  >
                    <span>View Task Verification</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                  {latestCompletedTask.github_pr_url && (
                    <a
                      href={latestCompletedTask.github_pr_url}
                      target="_blank"
                      rel="noreferrer"
                      className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow transition flex items-center space-x-1.5"
                    >
                      <GitPullRequest className="w-3.5 h-3.5" />
                      <span>Inspect PR</span>
                      <ExternalLink className="w-3 h-3 ml-0.5 opacity-70" />
                    </a>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Recent Engineering Tasks Card */}
          <div className="bg-[#0b1120] border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
            <div className="px-6 py-4 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-bold text-white">Recent Engineering Tasks</h3>
                <p className="text-xs text-slate-400">Live execution state of autonomous pipelines</p>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                {/* Search */}
                <div className="relative">
                  <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search tasks..."
                    className="bg-slate-950 border border-slate-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-blue-500 w-36 sm:w-44"
                  />
                </div>

                {/* Filter buttons */}
                <div className="flex items-center space-x-1 text-xs">
                  {(
                    [
                      { key: 'ALL', label: 'All' },
                      { key: 'ACTIVE', label: 'Active' },
                      { key: 'PENDING', label: 'Gates' },
                      { key: 'COMPLETED', label: 'Done' },
                    ] as const
                  ).map((item) => (
                    <button
                      key={item.key}
                      onClick={() => setFilter(item.key)}
                      className={`px-2.5 py-1 rounded-lg text-xs font-medium transition ${
                        filter === item.key
                          ? 'bg-blue-600 text-white shadow'
                          : 'text-slate-400 hover:text-white hover:bg-slate-800'
                      }`}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>

                <Link
                  href="/tasks/new"
                  className="text-xs font-semibold text-blue-400 hover:text-blue-300 pl-2 border-l border-slate-800"
                >
                  + Create
                </Link>
              </div>
            </div>

            {/* Task List Body */}
            {loading && tasks.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500">Loading active tasks...</div>
            ) : filteredTasks.length === 0 ? (
              <div className="p-12 text-center">
                <Layers className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                <p className="text-sm font-semibold text-slate-300">No tasks found matching criteria</p>
                <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                  Launch the demo task above or create a new task to see the six AI agents execute autonomously.
                </p>
              </div>
            ) : (
              <div className="divide-y divide-slate-800/60">
                {filteredTasks.slice(0, 8).map((task) => (
                  <Link
                    key={task.id}
                    href={`/tasks/${task.id}`}
                    className="block p-4 sm:px-6 hover:bg-slate-900/60 transition group"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div className="space-y-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-xs font-mono font-bold text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                            {task.id.slice(0, 8)}
                          </span>
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                              task.status === 'COMPLETED'
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                : task.status.includes('PENDING_APPROVAL')
                                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse'
                                : task.status.includes('FAILED')
                                ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                                : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                            }`}
                          >
                            {task.status.replace(/_/g, ' ')}
                          </span>

                          {task.retry_count > 0 && (
                            <span className="text-[10px] text-amber-400 bg-amber-950/40 px-1.5 py-0.5 rounded border border-amber-800/30 flex items-center space-x-1">
                              <Bug className="w-3 h-3" />
                              <span>{task.retry_count} {task.retry_count === 1 ? 'fix' : 'fixes'}</span>
                            </span>
                          )}
                        </div>

                        <h4 className="text-sm font-semibold text-white group-hover:text-blue-400 transition-colors">
                          {task.feature_request}
                        </h4>

                        <p className="text-xs text-slate-500 break-words max-w-xl">
                          Repository: <span className="font-mono text-slate-400 break-all">{task.repository}</span>
                        </p>
                      </div>

                      <div className="flex items-center space-x-4 self-end sm:self-center flex-shrink-0">
                        <div className="text-right text-xs text-slate-500">
                          <div>{new Date(task.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                        </div>
                        <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-blue-400 group-hover:translate-x-1 transition-all" />
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right / Telemetry & Agent Hierarchy Section (4 cols on desktop) */}
        <div className="lg:col-span-4 space-y-6">
          {/* Six Autonomous Agents Status Card */}
          <div className="bg-[#0b1120] border border-slate-800/80 rounded-2xl p-5 shadow-xl">
            <div className="flex items-center justify-between mb-4 pb-2.5 border-b border-slate-800/80">
              <h2 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                <Cpu className="w-4 h-4 text-blue-400" />
                <span>Six-Agent Hierarchy</span>
              </h2>
              <Link href="/agents" className="text-xs text-blue-400 hover:underline">
                Full specs &rarr;
              </Link>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-start justify-between gap-2">
                <div>
                  <div className="text-purple-400 font-bold flex items-center space-x-1.5">
                    <FileText className="w-3.5 h-3.5" />
                    <span>1. PRD Agent</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-tight mt-0.5">
                    Scope, acceptance tests & requirements
                  </p>
                </div>
                <span className="text-[10px] font-semibold text-amber-400/90 bg-amber-500/10 border border-amber-500/20 px-1.5 py-0.5 rounded whitespace-nowrap">
                  Gate 1
                </span>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-start justify-between gap-2">
                <div>
                  <div className="text-indigo-400 font-bold flex items-center space-x-1.5">
                    <Compass className="w-3.5 h-3.5" />
                    <span>2. Architect Agent</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-tight mt-0.5">
                    AST audit & file modification blueprint
                  </p>
                </div>
                <span className="text-[10px] font-semibold text-amber-400/90 bg-amber-500/10 border border-amber-500/20 px-1.5 py-0.5 rounded whitespace-nowrap">
                  Gate 2
                </span>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-start justify-between gap-2">
                <div>
                  <div className="text-blue-400 font-bold flex items-center space-x-1.5">
                    <Code2 className="w-3.5 h-3.5" />
                    <span>3. Developer Agent</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-tight mt-0.5">
                    Isolated Git sandbox code modifications
                  </p>
                </div>
                <span className="text-[10px] font-semibold text-emerald-400/90 bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 rounded whitespace-nowrap">
                  Sandbox
                </span>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-start justify-between gap-2">
                <div>
                  <div className="text-amber-400 font-bold flex items-center space-x-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>4. Tester Agent</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-tight mt-0.5">
                    Headless Playwright Chromium & visual QA
                  </p>
                </div>
                <span className="text-[10px] font-semibold text-teal-400/90 bg-teal-500/10 border border-teal-500/20 px-1.5 py-0.5 rounded whitespace-nowrap">
                  Browser
                </span>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-start justify-between gap-2">
                <div>
                  <div className="text-rose-400 font-bold flex items-center space-x-1.5">
                    <Bug className="w-3.5 h-3.5" />
                    <span>5. Debug / Fix Agent</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-tight mt-0.5">
                    Root cause diagnosis & surgical fix loops
                  </p>
                </div>
                <span className="text-[10px] font-semibold text-rose-400/90 bg-rose-500/10 border border-rose-500/20 px-1.5 py-0.5 rounded whitespace-nowrap">
                  Auto-Fix
                </span>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-start justify-between gap-2">
                <div>
                  <div className="text-teal-400 font-bold flex items-center space-x-1.5">
                    <GitPullRequest className="w-3.5 h-3.5" />
                    <span>6. Reviewer Agent</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-tight mt-0.5">
                    Diff audit & verified GitHub Pull Request
                  </p>
                </div>
                <span className="text-[10px] font-semibold text-indigo-400/90 bg-indigo-500/10 border border-indigo-500/20 px-1.5 py-0.5 rounded whitespace-nowrap">
                  Sign-Off
                </span>
              </div>
            </div>
          </div>

          {/* Live Telemetry & Platform Overview Card */}
          <div className="bg-[#0b1120] border border-slate-800/80 rounded-2xl p-5 shadow-xl space-y-4">
            <div className="flex items-center justify-between pb-2.5 border-b border-slate-800/80">
              <h2 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                <Activity className="w-4 h-4 text-emerald-400" />
                <span>Live Orchestration Telemetry</span>
              </h2>
              <span className="flex items-center space-x-1 text-[10px] text-emerald-400 font-mono">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Active</span>
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between text-slate-300">
                <span className="text-slate-400">Deterministic State Machine:</span>
                <span className="font-semibold text-white">FastAPI Engine</span>
              </div>
              <div className="flex items-center justify-between text-slate-300">
                <span className="text-slate-400">Human Approval Gates:</span>
                <span className="font-semibold text-amber-400">PRD + Architecture</span>
              </div>
              <div className="flex items-center justify-between text-slate-300">
                <span className="text-slate-400">Browser Test Automation:</span>
                <span className="font-semibold text-blue-400">Playwright Chromium</span>
              </div>
              <div className="flex items-center justify-between text-slate-300">
                <span className="text-slate-400">Workspace Sandboxing:</span>
                <span className="font-semibold text-emerald-400">Ephemeral / Isolated</span>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800/80">
              <Link
                href="/activity"
                className="w-full py-2 px-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white text-xs font-semibold border border-slate-800 transition flex items-center justify-center space-x-1.5"
              >
                <span>View Full Telemetry Stream</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
