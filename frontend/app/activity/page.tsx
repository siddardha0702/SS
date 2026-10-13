'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { fetchTasks } from '../../lib/api';
import { Task } from '../../types';
import {
  Activity,
  GitPullRequest,
  ShieldCheck,
  CheckCircle2,
  Bug,
  Clock,
  Terminal,
  ArrowRight,
  RefreshCw,
  Cpu,
  Layers,
} from 'lucide-react';

interface ActivityItem {
  id: string;
  taskId: string;
  taskTitle: string;
  type: 'PR' | 'GATE' | 'TEST' | 'CORRECTION' | 'TASK_CREATED' | 'RUNNING';
  agent: string;
  message: string;
  status: string;
  timestamp: string;
}

export default function ActivityPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'ALL' | 'GATES' | 'CORRECTIONS' | 'PRS'>('ALL');

  const loadData = async () => {
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
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  // Synthesize timeline items from real task state history
  const activities: ActivityItem[] = [];

  tasks.forEach((task) => {
    // 1. Task created
    activities.push({
      id: `${task.id}-created`,
      taskId: task.id,
      taskTitle: task.feature_request,
      type: 'TASK_CREATED',
      agent: 'System Orchestrator',
      message: `Initialized autonomous workspace for repository ${task.repository}`,
      status: 'completed',
      timestamp: task.created_at,
    });

    // 2. PRD Gate if completed or pending
    if (task.status.includes('PENDING_APPROVAL') || task.status === 'COMPLETED' || task.status.includes('DEVELOPMENT')) {
      activities.push({
        id: `${task.id}-prd`,
        taskId: task.id,
        taskTitle: task.feature_request,
        type: 'GATE',
        agent: 'PRD Agent',
        message: task.status === 'PRD_PENDING_APPROVAL' ? 'Awaiting Human Approval Gate 1' : 'PRD specification completed & signed off',
        status: task.status === 'PRD_PENDING_APPROVAL' ? 'pending' : 'passed',
        timestamp: task.updated_at,
      });
    }

    // 3. Self-correction if any
    if (task.retry_count > 0) {
      activities.push({
        id: `${task.id}-correction`,
        taskId: task.id,
        taskTitle: task.feature_request,
        type: 'CORRECTION',
        agent: 'Debug / Fix Agent',
        message: `Self-correction loop triggered (${task.retry_count} fix cycle${task.retry_count > 1 ? 's' : ''})`,
        status: 'fixed',
        timestamp: task.updated_at,
      });
    }

    // 4. Completed PR
    if (task.status === 'COMPLETED' && task.github_pr_url) {
      activities.push({
        id: `${task.id}-pr`,
        taskId: task.id,
        taskTitle: task.feature_request,
        type: 'PR',
        agent: 'Reviewer Agent',
        message: `Generated verified Pull Request on branch ${task.branch_name || 'feature'}`,
        status: 'verified',
        timestamp: task.updated_at,
      });
    }
  });

  // Sort descending by timestamp
  activities.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  const filtered = activities.filter((act) => {
    if (filter === 'GATES') return act.type === 'GATE';
    if (filter === 'CORRECTIONS') return act.type === 'CORRECTION';
    if (filter === 'PRS') return act.type === 'PR';
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2.5">
            <Activity className="w-6 h-6 text-blue-400" />
            <span>Autonomous Activity Stream</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time telemetry and milestone audit trail across all autonomous agent executions
          </p>
        </div>

        <button
          onClick={() => {
            setLoading(true);
            loadData();
          }}
          className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition self-start sm:self-auto"
          title="Refresh activity"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="bg-[#0b1120] border border-slate-800 rounded-2xl p-3 shadow-lg flex items-center space-x-1 text-xs overflow-x-auto">
        {(
          [
            { key: 'ALL', label: `All Events (${activities.length})` },
            { key: 'GATES', label: 'Human Gates' },
            { key: 'CORRECTIONS', label: 'Self-Corrections' },
            { key: 'PRS', label: 'Verified Pull Requests' },
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

      {/* Stream List */}
      <div className="bg-[#0b1120] border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        {loading && activities.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-slate-600" />
            <span>Loading telemetry stream...</span>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center space-y-2">
            <Activity className="w-8 h-8 text-slate-600 mx-auto" />
            <h3 className="text-sm font-semibold text-slate-300">No events matching filter</h3>
            <p className="text-xs text-slate-500">Agent milestones will stream in live as tasks execute.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-800/60">
            {filtered.map((item) => {
              const isPR = item.type === 'PR';
              const isGate = item.type === 'GATE';
              const isCorrection = item.type === 'CORRECTION';

              return (
                <div key={item.id} className="p-4 sm:px-6 hover:bg-slate-900/40 transition">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-start space-x-3">
                      <div className="p-2 rounded-xl bg-slate-900 border border-slate-800 mt-0.5">
                        {isPR ? (
                          <GitPullRequest className="w-4 h-4 text-emerald-400" />
                        ) : isGate ? (
                          <ShieldCheck className="w-4 h-4 text-amber-400" />
                        ) : isCorrection ? (
                          <Bug className="w-4 h-4 text-rose-400" />
                        ) : (
                          <Cpu className="w-4 h-4 text-blue-400" />
                        )}
                      </div>

                      <div className="space-y-0.5">
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-bold text-white">{item.agent}</span>
                          <span
                            className={`text-[10px] px-2 py-0.2 rounded-full font-semibold uppercase tracking-wider ${
                              item.status === 'verified' || item.status === 'passed'
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                : item.status === 'pending'
                                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse'
                                : item.status === 'fixed'
                                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                : 'bg-slate-800 text-slate-400'
                            }`}
                          >
                            {item.status}
                          </span>
                        </div>

                        <p className="text-xs text-slate-300">{item.message}</p>

                        <div className="text-[11px] text-slate-500 flex items-center space-x-2">
                          <span>Task:</span>
                          <Link
                            href={`/tasks/${item.taskId}`}
                            className="text-blue-400 hover:underline truncate max-w-sm"
                          >
                            {item.taskTitle}
                          </Link>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3 self-end sm:self-center text-xs text-slate-500">
                      <span>{new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                      <Link
                        href={`/tasks/${item.taskId}`}
                        className="text-slate-400 hover:text-white"
                        title="View task"
                      >
                        <ArrowRight className="w-4 h-4" />
                      </Link>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
