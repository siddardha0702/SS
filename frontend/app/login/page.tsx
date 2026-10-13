'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Cpu,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Lock,
  Mail,
  Github,
  Eye,
  EyeOff,
  AlertCircle,
  Play,
  Terminal,
  Layers,
} from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('demo.engineer@nexus.ai');
  const [password, setPassword] = useState('••••••••••••');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // Simulated guest/demo login transition
    setTimeout(() => {
      router.push('/');
    }, 600);
  };

  const handleGitHubAuth = () => {
    setLoading(true);
    setTimeout(() => {
      router.push('/');
    }, 600);
  };

  const handleForgotPassword = (e: React.MouseEvent) => {
    e.preventDefault();
    setNotice('Password recovery in evaluation mode: Use any test credentials or click "Instant Guest Access".');
  };

  return (
    <div className="min-h-[80vh] flex flex-col justify-center items-center py-6">
      <div className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        {/* Left column: SaaS Product Pitch & Architecture Highlights */}
        <div className="lg:col-span-7 space-y-6">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-xs font-semibold text-blue-400">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Autonomous AI Software Engineering Team</span>
          </div>

          <div className="space-y-2">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight leading-tight">
              Ship Verified Code with <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-cyan-300 bg-clip-text text-transparent">Autonomous AI</span>
            </h1>
            <p className="text-sm sm:text-base text-slate-300 leading-relaxed pt-2">
              Nexus transforms high-level engineering requests into verified, production-ready Pull Requests.
              A coordinated hierarchy of six specialized AI agents handles PRD generation, architectural blueprinting,
              isolated coding, Playwright browser testing, and autonomous self-correction.
            </p>
          </div>

          {/* Key Value Pillars */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <div className="flex items-center space-x-2 text-xs font-bold text-white mb-1">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Deterministic 6-Agent Tree</span>
              </div>
              <p className="text-[11px] text-slate-400">
                PRD, Architect, Developer, Tester, Debug, and Reviewer agents in a strict state machine.
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <div className="flex items-center space-x-2 text-xs font-bold text-white mb-1">
                <ShieldCheck className="w-4 h-4 text-blue-400" />
                <span>Two Human Approval Gates</span>
              </div>
              <p className="text-[11px] text-slate-400">
                You retain complete control: approve or revise PRD (Gate 1) and Architecture (Gate 2).
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <div className="flex items-center space-x-2 text-xs font-bold text-white mb-1">
                <Terminal className="w-4 h-4 text-amber-400" />
                <span>Playwright Browser Tests</span>
              </div>
              <p className="text-[11px] text-slate-400">
                Headless Chromium boots the web app, validates DOM elements, and captures screenshots.
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
              <div className="flex items-center space-x-2 text-xs font-bold text-white mb-1">
                <Layers className="w-4 h-4 text-rose-400" />
                <span>Autonomous Self-Correction</span>
              </div>
              <p className="text-[11px] text-slate-400">
                Playwright failures trigger the Debug Agent to diagnose root cause and apply surgical fixes.
              </p>
            </div>
          </div>

          <div className="pt-2 flex items-center space-x-3 text-xs text-slate-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Production-grade sandbox isolation &bull; Real GitHub Pull Requests</span>
          </div>
        </div>

        {/* Right column: SaaS Authentication UI Card */}
        <div className="lg:col-span-5">
          <div className="bg-[#0b1120] border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-5 relative">
            {/* Logo / Header */}
            <div className="text-center space-y-1">
              <div className="inline-flex w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 items-center justify-center text-white shadow-lg shadow-blue-500/20 mb-2">
                <Cpu className="w-6 h-6" />
              </div>
              <h2 className="text-xl font-bold text-white tracking-tight">
                {isSignUp ? 'Create Nexus Account' : 'Welcome to Nexus Console'}
              </h2>
              <p className="text-xs text-slate-400">
                {isSignUp
                  ? 'Join your team’s autonomous engineering workspace'
                  : 'Enter your credentials to access the multi-agent console'}
              </p>
            </div>

            {/* Tab switch between Sign In and Create Account */}
            <div className="grid grid-cols-2 p-1 bg-slate-900 rounded-xl border border-slate-800 text-xs font-semibold">
              <button
                type="button"
                onClick={() => setIsSignUp(false)}
                className={`py-1.5 rounded-lg transition ${
                  !isSignUp ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => setIsSignUp(true)}
                className={`py-1.5 rounded-lg transition ${
                  isSignUp ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'
                }`}
              >
                Create Account
              </button>
            </div>

            {/* Demo Notice Banner (Transparent & Honest) */}
            <div className="p-3 rounded-xl bg-blue-950/40 border border-blue-500/30 text-xs text-blue-300/90 leading-relaxed">
              <div className="flex items-center space-x-1.5 font-semibold text-blue-300 mb-0.5">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>Evaluation Environment</span>
              </div>
              <span>
                Authentication is presented for SaaS workflow demonstration. Clicking Sign In enters the workspace with full administrative privileges.
              </span>
            </div>

            {notice && (
              <div className="p-2.5 rounded-lg bg-amber-950/40 border border-amber-500/30 text-xs text-amber-300">
                {notice}
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-3.5">
              <div>
                <label className="block text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-1">
                  Work Email
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="name@company.com"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-1">
                  Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    placeholder="••••••••••••"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-10 py-2.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-blue-500 font-mono"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 top-3 text-slate-500 hover:text-slate-300"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs pt-1">
                <label className="flex items-center space-x-2 text-slate-400 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="rounded bg-slate-950 border-slate-800 text-blue-600 focus:ring-0"
                  />
                  <span>Remember me</span>
                </label>
                <button
                  type="button"
                  onClick={handleForgotPassword}
                  className="text-blue-400 hover:text-blue-300 transition text-[11px]"
                >
                  Forgot password?
                </button>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-blue-600/30 transition flex items-center justify-center space-x-2 disabled:opacity-50"
              >
                <span>{isSignUp ? 'Create Account & Enter' : 'Sign In & Enter Console'}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </form>

            {/* Divider */}
            <div className="relative flex items-center justify-center">
              <div className="border-t border-slate-800 w-full"></div>
              <span className="bg-[#0b1120] px-3 text-[10px] text-slate-500 uppercase tracking-wider absolute">
                or continue with
              </span>
            </div>

            {/* Social / SSO Button */}
            <button
              type="button"
              onClick={handleGitHubAuth}
              disabled={loading}
              className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-white text-xs font-semibold transition flex items-center justify-center space-x-2"
            >
              <Github className="w-4 h-4" />
              <span>Continue with GitHub</span>
            </button>

            {/* Quick Guest Access Button */}
            <div className="pt-1 text-center">
              <Link
                href="/"
                className="inline-flex items-center space-x-1.5 text-xs text-slate-400 hover:text-blue-400 font-semibold transition"
              >
                <span>Skip authentication &rarr; Instant Guest Access</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
