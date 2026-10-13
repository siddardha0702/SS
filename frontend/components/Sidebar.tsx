'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Cpu,
  LayoutDashboard,
  PlusCircle,
  Layers,
  Activity,
  Settings,
  HelpCircle,
  ChevronRight,
  ShieldCheck,
  Radio,
  Sparkles,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  const navItems = [
    { label: 'Dashboard', href: '/', icon: LayoutDashboard },
    { label: 'New Task', href: '/tasks/new', icon: PlusCircle },
    { label: 'All Tasks', href: '/tasks', icon: Layers },
    { label: 'Six Agents', href: '/agents', icon: Cpu },
    { label: 'Live Activity', href: '/activity', icon: Activity },
    { label: 'System Guide', href: '/help', icon: HelpCircle },
    { label: 'Settings', href: '/settings', icon: Settings },
  ];

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/';
    return pathname.startsWith(href);
  };

  return (
    <aside className="hidden md:flex flex-col w-64 shrink-0 bg-[#070b14] border-r border-slate-800/80 h-screen sticky top-0 overflow-y-auto z-30 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80">
        <Link href="/" className="flex items-center space-x-3 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 flex items-center justify-center font-black text-white shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="font-bold tracking-tight text-white text-base">NEXUS</span>
              <span className="px-1.5 py-0.2 text-[9px] uppercase font-bold tracking-wider rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                v1.0
              </span>
            </div>
            <p className="text-[10px] text-slate-400">Autonomous AI Team</p>
          </div>
        </Link>
      </div>

      {/* Main Navigation */}
      <div className="flex-1 px-3 py-4 space-y-6">
        <div>
          <div className="px-3 mb-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
            Platform Navigation
          </div>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const active = isActive(item.href);
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                    active
                      ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 font-semibold shadow-sm'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon className={`w-4 h-4 ${active ? 'text-blue-400' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </div>
                  {active && <ChevronRight className="w-3.5 h-3.5 text-blue-400/80" />}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* System Health / Agent Engine Status */}
        <div className="px-3">
          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Agent Engine
              </span>
              <span className="flex items-center space-x-1 text-[10px] text-emerald-400 font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Active</span>
              </span>
            </div>
            <p className="text-[11px] text-slate-300 leading-tight">
              6 autonomous agents with 2 human approval gates enforced.
            </p>
            <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500 font-mono">
              <span>Mode: Demo</span>
              <span className="text-blue-400">Deterministic</span>
            </div>
          </div>
        </div>

        {/* Quick Launch Action */}
        <div className="px-3">
          <Link
            href="/tasks/new"
            className="w-full py-2.5 px-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-md shadow-blue-600/20 transition flex items-center justify-center space-x-2"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Launch New Task</span>
          </Link>
        </div>
      </div>

      {/* User / Session Footer */}
      <div className="p-3 border-t border-slate-800/80">
        <Link
          href="/settings"
          className="flex items-center space-x-3 p-2 rounded-xl hover:bg-slate-900 transition text-left w-full"
        >
          <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-600 flex items-center justify-center text-[10px] font-bold text-white shrink-0">
            DE
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-xs font-semibold text-white truncate">Demo User</div>
            <div className="text-[10px] text-slate-400 truncate">Staff AI Engineer</div>
          </div>
        </Link>
      </div>
    </aside>
  );
};
