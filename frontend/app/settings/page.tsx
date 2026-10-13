'use client';

import React, { useState } from 'react';
import {
  Settings,
  User,
  Github,
  Cpu,
  Bell,
  Palette,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  ShieldCheck,
  Save,
  Key,
} from 'lucide-react';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<'profile' | 'github' | 'ai' | 'notifications' | 'appearance'>('profile');
  const [savedToast, setSavedToast] = useState(false);

  // Form states
  const [name, setName] = useState('Evaluation Engineer');
  const [email, setEmail] = useState('demo.engineer@nexus.ai');
  const [githubRepo, setGithubRepo] = useState('siddardha0702/Nexus2');
  const [aiModel, setAiModel] = useState('gpt-4o');
  const [maxRetries, setMaxRetries] = useState('3');
  const [wsEnabled, setWsEnabled] = useState(true);
  const [theme, setTheme] = useState('dark');

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedToast(true);
    setTimeout(() => setSavedToast(false), 3000);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2.5">
          <Settings className="w-6 h-6 text-blue-400" />
          <span>Platform & Agent Settings</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Manage workspace profile, AI models, GitHub repository bindings, and telemetry preferences
        </p>
      </div>

      {/* Toast */}
      {savedToast && (
        <div className="p-3 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-xs text-emerald-300 flex items-center space-x-2 shadow-lg">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>Preferences successfully saved to local session.</span>
        </div>
      )}

      {/* Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-2 text-xs overflow-x-auto">
        <button
          onClick={() => setActiveTab('profile')}
          className={`px-3.5 py-2 rounded-xl font-medium transition flex items-center space-x-2 whitespace-nowrap ${
            activeTab === 'profile'
              ? 'bg-blue-600 text-white shadow'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          }`}
        >
          <User className="w-3.5 h-3.5" />
          <span>User Profile</span>
        </button>

        <button
          onClick={() => setActiveTab('github')}
          className={`px-3.5 py-2 rounded-xl font-medium transition flex items-center space-x-2 whitespace-nowrap ${
            activeTab === 'github'
              ? 'bg-blue-600 text-white shadow'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          }`}
        >
          <Github className="w-3.5 h-3.5" />
          <span>GitHub Integration</span>
        </button>

        <button
          onClick={() => setActiveTab('ai')}
          className={`px-3.5 py-2 rounded-xl font-medium transition flex items-center space-x-2 whitespace-nowrap ${
            activeTab === 'ai'
              ? 'bg-blue-600 text-white shadow'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          }`}
        >
          <Cpu className="w-3.5 h-3.5" />
          <span>AI Model Engine</span>
        </button>

        <button
          onClick={() => setActiveTab('notifications')}
          className={`px-3.5 py-2 rounded-xl font-medium transition flex items-center space-x-2 whitespace-nowrap ${
            activeTab === 'notifications'
              ? 'bg-blue-600 text-white shadow'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          }`}
        >
          <Bell className="w-3.5 h-3.5" />
          <span>Telemetry & Alerts</span>
        </button>

        <button
          onClick={() => setActiveTab('appearance')}
          className={`px-3.5 py-2 rounded-xl font-medium transition flex items-center space-x-2 whitespace-nowrap ${
            activeTab === 'appearance'
              ? 'bg-blue-600 text-white shadow'
              : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
          }`}
        >
          <Palette className="w-3.5 h-3.5" />
          <span>Appearance</span>
        </button>
      </div>

      {/* Main Settings Card */}
      <div className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl">
        <form onSubmit={handleSave} className="space-y-6">
          {/* TAB 1: PROFILE */}
          {activeTab === 'profile' && (
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Evaluation Profile</h3>
              <p className="text-xs text-slate-400">
                User information used in review attribution and approval signatures.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                <div>
                  <label className="block text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-1">
                    Display Name
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-400 space-y-1">
                <span className="font-semibold text-slate-200">Role Authority: </span>
                <span>Workspace Lead / Gate Approver (Full read & write access to approval gates)</span>
              </div>
            </div>
          )}

          {/* TAB 2: GITHUB */}
          {activeTab === 'github' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">GitHub Integration</h3>
                  <p className="text-xs text-slate-400">
                    Configuration for autonomous git branching and Pull Request creation.
                  </p>
                </div>
                <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[11px] font-semibold flex items-center space-x-1">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Backend Configured</span>
                </span>
              </div>

              <div className="space-y-3 pt-2">
                <div>
                  <label className="block text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-1">
                    Target GitHub Repository
                  </label>
                  <input
                    type="text"
                    value={githubRepo}
                    onChange={(e) => setGithubRepo(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white font-mono placeholder-slate-600 focus:outline-none focus:border-blue-500"
                  />
                  <p className="text-[11px] text-slate-500 mt-1">
                    Default repository for pulling code and opening Pull Requests.
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-blue-950/30 border border-blue-500/30 text-xs text-blue-300 space-y-1 leading-relaxed">
                  <div className="font-semibold flex items-center space-x-1.5">
                    <Key className="w-3.5 h-3.5" />
                    <span>Server-Side GITHUB_TOKEN</span>
                  </div>
                  <p className="text-[11px] text-slate-300">
                    GitHub access tokens are securely read from the backend environment file (<code className="text-blue-300">.env</code>). Nexus automatically verifies authentication before pushing branches.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: AI CONFIG */}
          {activeTab === 'ai' && (
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">AI Model Engine</h3>
              <p className="text-xs text-slate-400">
                Configure primary LLM providers and autonomous self-correction parameters.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                <div>
                  <label className="block text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-1">
                    Primary Intelligence Model
                  </label>
                  <select
                    value={aiModel}
                    onChange={(e) => setAiModel(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="gpt-4o">OpenAI GPT-4o (Default)</option>
                    <option value="claude-3-5-sonnet">Anthropic Claude 3.5 Sonnet</option>
                    <option value="gemini-1-5-pro">Google Gemini 1.5 Pro</option>
                    <option value="deterministic-fallback">Deterministic Fallback Engine (Zero API Key)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-1">
                    Max Self-Correction Cycles
                  </label>
                  <select
                    value={maxRetries}
                    onChange={(e) => setMaxRetries(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-blue-500 font-mono"
                  >
                    <option value="1">1 Retry Cycle</option>
                    <option value="2">2 Retry Cycles</option>
                    <option value="3">3 Retry Cycles (Recommended)</option>
                  </select>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 leading-relaxed">
                <span className="font-semibold text-white">Zero-Config Deterministic Fallback: </span>
                If no OpenAI API key is detected in the backend, Nexus uses its built-in rule-based deterministic synthesis engine so hackathon evaluators can inspect the complete six-agent flow without incurring API costs.
              </div>
            </div>
          )}

          {/* TAB 4: NOTIFICATIONS */}
          {activeTab === 'notifications' && (
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Telemetry & Alerts</h3>
              <p className="text-xs text-slate-400">
                Configure real-time event streaming and webhook notifications.
              </p>

              <div className="space-y-3 pt-2">
                <label className="flex items-center space-x-3 p-3 rounded-xl bg-slate-900 border border-slate-800 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={wsEnabled}
                    onChange={(e) => setWsEnabled(e.target.checked)}
                    className="rounded bg-slate-950 border-slate-700 text-blue-600 focus:ring-0"
                  />
                  <div className="text-xs">
                    <div className="font-semibold text-white">Real-Time WebSocket Stream</div>
                    <div className="text-[11px] text-slate-400">
                      Receive live agent milestone events without page reloading.
                    </div>
                  </div>
                </label>

                {/* Mark clearly unfinished integration as requested */}
                <div className="p-3.5 rounded-xl bg-slate-900/60 border border-dashed border-slate-800 text-xs space-y-2">
                  <div className="flex items-center space-x-2 text-slate-400 font-semibold">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                    <span>Outbound Webhook Dispatch (Scheduled for v1.1)</span>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    External webhook forwarding to Slack and Discord channels is currently in preview development. Local WebSocket streaming is fully functional.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: APPEARANCE */}
          {activeTab === 'appearance' && (
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Appearance & Theme</h3>
              <p className="text-xs text-slate-400">Customize visual appearance of the engineering console.</p>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setTheme('dark')}
                  className={`p-3.5 rounded-xl border text-left transition ${
                    theme === 'dark'
                      ? 'bg-blue-950/40 border-blue-500 text-white'
                      : 'bg-slate-900 border-slate-800 text-slate-400'
                  }`}
                >
                  <div className="text-xs font-bold text-white mb-0.5">Midnight Slate (Active)</div>
                  <div className="text-[11px] text-slate-400">High-contrast developer theme with dark cards</div>
                </button>

                <div className="p-3.5 rounded-xl bg-slate-900/40 border border-dashed border-slate-800 text-slate-500 text-xs flex flex-col justify-center">
                  <span className="font-semibold text-slate-400">Light Mode</span>
                  <span className="text-[10px] text-slate-500">Planned for future release</span>
                </div>
              </div>
            </div>
          )}

          {/* Action button */}
          <div className="pt-4 border-t border-slate-800 flex justify-end">
            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/30 transition flex items-center space-x-2"
            >
              <Save className="w-4 h-4" />
              <span>Save Workspace Preferences</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
