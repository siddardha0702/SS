import React from 'react';
import Link from 'next/link';
import { Cpu, Github, ExternalLink, ShieldCheck, Heart } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800/80 bg-[#070b13] text-slate-400 text-xs mt-auto">
      <div className="w-full max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand info */}
          <div className="md:col-span-1 space-y-3">
            <div className="flex items-center space-x-2.5">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white">
                <Cpu className="w-4 h-4" />
              </div>
              <span className="font-bold text-white text-base tracking-tight">NEXUS</span>
              <span className="text-[10px] bg-blue-500/10 text-blue-400 border border-blue-500/20 px-1.5 py-0.2 rounded font-mono">
                v1.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Autonomous AI Software Engineering Team. End-to-end autonomous pipeline from PRD to verified Pull Requests with Playwright browser verification.
            </p>
            <div className="flex items-center space-x-2 text-[11px] text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>All 6 Autonomous Agents Operational</span>
            </div>
          </div>

          {/* Navigation Links */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">Platform</h4>
            <ul className="space-y-2 text-[11px]">
              <li>
                <Link href="/" className="hover:text-blue-400 transition">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/tasks/new" className="hover:text-blue-400 transition">
                  Launch New Task
                </Link>
              </li>
              <li>
                <Link href="/tasks" className="hover:text-blue-400 transition">
                  All Tasks & Workspaces
                </Link>
              </li>
              <li>
                <Link href="/agents" className="hover:text-blue-400 transition">
                  Six-Agent Architecture
                </Link>
              </li>
              <li>
                <Link href="/activity" className="hover:text-blue-400 transition">
                  Live Activity Stream
                </Link>
              </li>
            </ul>
          </div>

          {/* Engineering & Docs */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">Architecture</h4>
            <ul className="space-y-2 text-[11px]">
              <li>
                <Link href="/help" className="hover:text-blue-400 transition">
                  System Architecture Guide
                </Link>
              </li>
              <li>
                <Link href="/help#human-gates" className="hover:text-blue-400 transition">
                  Two Human Approval Gates
                </Link>
              </li>
              <li>
                <Link href="/help#self-correction" className="hover:text-blue-400 transition">
                  Playwright Self-Correction Loop
                </Link>
              </li>
              <li>
                <Link href="/help#security" className="hover:text-blue-400 transition">
                  Workspace Sandboxing & Safety
                </Link>
              </li>
              <li>
                <Link href="/settings" className="hover:text-blue-400 transition">
                  Environment & AI Settings
                </Link>
              </li>
            </ul>
          </div>

          {/* Destination & Access */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">Project & Access</h4>
            <ul className="space-y-2 text-[11px]">
              <li>
                <Link href="/login" className="hover:text-blue-400 transition flex items-center space-x-1">
                  <span>Demo Login Portal</span>
                </Link>
              </li>
              <li>
                <a
                  href="https://github.com/siddardha0702/Nexus2"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-blue-400 transition flex items-center space-x-1"
                >
                  <Github className="w-3.5 h-3.5" />
                  <span>GitHub: siddardha0702/Nexus2</span>
                  <ExternalLink className="w-2.5 h-2.5 ml-0.5 opacity-60" />
                </a>
              </li>
              <li className="text-slate-500 pt-1">
                <span className="font-mono text-[10px]">Deterministic Multi-Agent State Machine</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-6 border-t border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-slate-500">
          <div>
            Nexus Autonomous Engineering System &copy; {new Date().getFullYear()} &bull; Built for Autonomous Software Engineering
          </div>
          <div className="flex items-center space-x-4">
            <span className="hover:text-slate-400 cursor-pointer">Privacy & Sandbox Isolation</span>
            <span>&bull;</span>
            <span className="hover:text-slate-400 cursor-pointer">Evaluation Terms</span>
            <span>&bull;</span>
            <span className="text-emerald-400/80">API v1.0 Connected</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
