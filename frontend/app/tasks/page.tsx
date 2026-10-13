'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { fetchTasks } from '../../lib/api';
import { Task } from '../../types';
import {
  Layers,
  PlusCircle,
  Search,
  Filter,
  ArrowRight,
  GitPullRequest,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Bug,
  RefreshCw,
  FolderGit2,
} from 'lucide-react';

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'ALL' | 'ACTIVE' | 'PENDING' | 'COMPLETED' | 'FAILED'>('ALL');

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
    const interval = setInterval(loadTasks, 5000);
    return () => clearInterval(interval);
  }, []);

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

  const completedCount = tasks.filter((t) => t.status === 'COMPLETED').length;
  const activeCount = tasks.filter((t) => !['COMPLETED', 'CANCELLED'].includes(t.status) && !t.status.includes('FAILED')).length;
  const pendingCount = tasks.filter((t) => t.status.includes('PENDING_APPROVAL')).length;
  const retriesCount = tasks.reduce((sum, t) => sum + (t.retry_count || 0), 0);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2.5">
            <Layers className="w-6 h-6 text-blue-400" />
            <span>Tasks & Engineering Workspaces</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Browse and monitor autonomous multi-agent engineering workflows across your repositories
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => {
              setLoading(true);
              loadTasks();
            }}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition"
            title="Refresh tasks"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <Link
            href="/tasks/new"
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/30 transition flex items-center space-x-1.5"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Create Task</span>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div className="bg-[#0b1120] border border-slate-800/80 rounded-2xl p-4 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Total Tasks</span>
            <Layers className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white font-mono">{tasks.length}</div>
        </div>

        <div className="bg-[#0b1120] border border-slate-800/80 rounded-2xl p-4 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Active Pipelines</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400 font-mono">{activeCount}</div>
        </div>

        <div className="bg-[#0b1120] border border-slate-800/80 rounded-2xl p-4 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Pending Gates</span>
            <AlertTriangle className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-amber-500 font-mono">{pendingCount}</div>
        </div>

        <div className="bg-[#0b1120] border border-slate-800/80 rounded-2xl p-4 shadow-lg">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Completed PRs</span>
            <GitPullRequest className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400 font-mono">{completedCount}</div>
        </div>
      </div>

      {/* Search and Filters Bar */}
      <div className="bg-[#0b1120] border border-slate-800 rounded-2xl p-4 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-3">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search tasks by description, repository, or ID..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 text-xs">
          {(
            [
              { key: 'ALL', label: `All (${tasks.length})` },
              { key: 'ACTIVE', label: `Active (${activeCount})` },
              { key: 'PENDING', label: `Pending Gate (${pendingCount})` },
              { key: 'COMPLETED', label: `Completed (${completedCount})` },
              { key: 'FAILED', label: 'Failed' },
            ] as const
          ).map((item) => (
            <button
              key={item.key}
              onClick={() => setFilter(item.key)}
              className={`px-3 py-1.5 rounded-lg font-medium whitespace-nowrap transition ${
                filter === item.key
                  ? 'bg-blue-600 text-white shadow'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* Task List Table */}
      <div className="bg-[#0b1120] border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        {loading && tasks.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-slate-600" />
            <span>Loading engineering tasks...</span>
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <Layers className="w-8 h-8 text-slate-600 mx-auto" />
            <h3 className="text-sm font-semibold text-slate-300">No matching tasks found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              {search || filter !== 'ALL'
                ? 'Try adjusting your search query or status filter to see other tasks.'
                : 'Get started by creating your first autonomous engineering task.'}
            </p>
            <Link
              href="/tasks/new"
              className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-blue-600 text-white text-xs font-semibold shadow hover:bg-blue-500 transition"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Launch New Task</span>
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-slate-800/60">
            {filteredTasks.map((task) => (
              <Link
                key={task.id}
                href={`/tasks/${task.id}`}
                className="block p-4 sm:px-6 hover:bg-slate-900/60 transition group"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="space-y-1.5 flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-xs font-mono font-bold text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                        {task.id.slice(0, 8)}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider ${
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
                        <span className="text-[10px] text-rose-300 bg-rose-950/40 px-2 py-0.5 rounded-full border border-rose-800/30 font-semibold flex items-center space-x-1">
                          <Bug className="w-3 h-3" />
                          <span>{task.retry_count} {task.retry_count === 1 ? 'correction' : 'corrections'}</span>
                        </span>
                      )}

                      {task.branch_name && (
                        <span className="text-[10px] text-slate-400 font-mono bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                          {task.branch_name}
                        </span>
                      )}
                    </div>

                    <h3 className="text-sm font-semibold text-white group-hover:text-blue-400 transition-colors leading-snug">
                      {task.feature_request}
                    </h3>

                    <div className="flex items-center space-x-4 text-xs text-slate-500">
                      <span className="flex items-center space-x-1 truncate max-w-sm">
                        <FolderGit2 className="w-3.5 h-3.5 text-slate-500" />
                        <span className="font-mono text-slate-400">{task.repository}</span>
                      </span>
                      <span>&bull;</span>
                      <span>{new Date(task.created_at).toLocaleDateString()} {new Date(task.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3 self-end sm:self-center flex-shrink-0">
                    <span className="text-xs font-semibold text-blue-400 group-hover:underline">
                      View Pipeline
                    </span>
                    <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-blue-400 group-hover:translate-x-1 transition-all" />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
