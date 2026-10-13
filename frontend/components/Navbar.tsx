'use client';

import React, { useState } from 'react';
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
  Menu,
  X,
  ChevronDown,
  ShieldCheck,
  LogOut,
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);

  const navItems = [
    { label: 'Dashboard', href: '/', icon: LayoutDashboard },
    { label: 'New Task', href: '/tasks/new', icon: PlusCircle },
    { label: 'Tasks', href: '/tasks', icon: Layers },
    { label: 'Agents', href: '/agents', icon: Cpu },
    { label: 'Activity', href: '/activity', icon: Activity },
    { label: 'Settings', href: '/settings', icon: Settings },
    { label: 'Help', href: '/help', icon: HelpCircle },
  ];

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/';
    return pathname.startsWith(href);
  };

  const getPageTitle = () => {
    if (pathname === '/') return 'Autonomous Engineering Dashboard';
    if (pathname === '/tasks/new') return 'Launch New Autonomous Task';
    if (pathname === '/tasks') return 'Engineering Tasks & Workspaces';
    if (pathname.startsWith('/tasks/')) return 'Task Telemetry & Verification';
    if (pathname === '/agents') return 'Six-Agent Autonomous Architecture';
    if (pathname === '/activity') return 'Live Telemetry & Activity Stream';
    if (pathname === '/settings') return 'Platform & Model Configuration';
    if (pathname === '/help') return 'System Architecture Documentation';
    if (pathname === '/login') return 'Demo Login Portal';
    return 'Nexus Platform Console';
  };

  return (
    <header className="border-b border-slate-800/80 bg-[#090d16]/95 backdrop-blur sticky top-0 z-40">
      <div className="w-full px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Left: Mobile Brand & Desktop Breadcrumb */}
        <div className="flex items-center space-x-3">
          {/* Mobile brand (hidden on md+ where desktop sidebar is visible) */}
          <Link href="/" className="flex md:hidden items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 flex items-center justify-center font-black text-white shadow">
              <Cpu className="w-4 h-4" />
            </div>
            <div>
              <span className="font-bold tracking-tight text-white text-base">NEXUS</span>
              <span className="ml-1.5 px-1.5 py-0.2 text-[9px] uppercase font-bold tracking-wider rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                v1.0
              </span>
            </div>
          </Link>

          {/* Desktop view header / breadcrumb */}
          <div className="hidden md:flex items-center space-x-2 text-xs text-slate-400">
            <span className="text-slate-500 font-mono">Console</span>
            <span className="text-slate-600">/</span>
            <span className="font-semibold text-slate-200">{getPageTitle()}</span>
          </div>
        </div>

        {/* Right Section: System status, New Task CTA, User Profile, Mobile Hamburger */}
        <div className="flex items-center space-x-3">
          {/* System Health Status Pill */}
          <div className="hidden sm:flex items-center space-x-2 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px]">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-slate-300">6 Agents Online</span>
          </div>

          {/* Primary CTA */}
          <Link
            href="/tasks/new"
            className="hidden sm:flex px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-600/30 transition items-center space-x-1.5"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>New Task</span>
          </Link>

          {/* User Profile Dropdown */}
          <div className="relative">
            <button
              onClick={() => setUserDropdownOpen(!userDropdownOpen)}
              className="flex items-center space-x-2 p-1.5 sm:px-2.5 sm:py-1 rounded-lg border border-slate-800 bg-slate-900/60 hover:bg-slate-800 text-slate-300 hover:text-white transition text-xs"
              title="User Account Menu"
            >
              <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-600 flex items-center justify-center text-[11px] font-bold text-white">
                DE
              </div>
              <span className="hidden lg:inline font-medium">Demo User</span>
              <ChevronDown className="w-3 h-3 text-slate-400 hidden sm:inline" />
            </button>

            {userDropdownOpen && (
              <div
                className="absolute right-0 mt-2 w-56 rounded-xl bg-slate-900 border border-slate-800 shadow-2xl py-1 z-50 text-xs"
                onClick={() => setUserDropdownOpen(false)}
              >
                <div className="px-3.5 py-2.5 border-b border-slate-800">
                  <div className="font-semibold text-white">Staff AI Engineer</div>
                  <div className="text-[11px] text-slate-400 font-mono">demo@nexus.ai</div>
                  <div className="mt-1 inline-flex items-center space-x-1 text-[10px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                    <ShieldCheck className="w-2.5 h-2.5" />
                    <span>Workspace Admin</span>
                  </div>
                </div>
                <Link
                  href="/settings"
                  className="px-3.5 py-2 hover:bg-slate-800 flex items-center space-x-2 text-slate-300 hover:text-white"
                >
                  <Settings className="w-3.5 h-3.5 text-slate-400" />
                  <span>Account & Preferences</span>
                </Link>
                <Link
                  href="/help"
                  className="px-3.5 py-2 hover:bg-slate-800 flex items-center space-x-2 text-slate-300 hover:text-white"
                >
                  <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
                  <span>Documentation & Architecture</span>
                </Link>
                <div className="border-t border-slate-800 my-1"></div>
                <Link
                  href="/login"
                  className="px-3.5 py-2 hover:bg-slate-800 flex items-center space-x-2 text-slate-400 hover:text-amber-400"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span>Switch User / Login Portal</span>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Hamburger Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-800 bg-[#090d16] px-4 pt-3 pb-5 space-y-2">
          <div className="grid grid-cols-2 gap-1.5 mb-3">
            {navItems.map((item) => {
              const active = isActive(item.href);
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`p-2.5 rounded-lg text-xs font-medium transition flex items-center space-x-2 ${
                    active
                      ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 font-semibold'
                      : 'text-slate-300 hover:bg-slate-800'
                  }`}
                >
                  <Icon className="w-4 h-4 text-slate-400" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>

          <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between gap-2">
            <Link
              href="/tasks/new"
              onClick={() => setMobileMenuOpen(false)}
              className="flex-1 py-2 px-3 rounded-lg bg-blue-600 text-white text-xs font-semibold text-center flex items-center justify-center space-x-1.5 shadow"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>Launch New Task</span>
            </Link>
            <Link
              href="/login"
              onClick={() => setMobileMenuOpen(false)}
              className="py-2 px-3 rounded-lg bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-700"
            >
              Portal
            </Link>
          </div>
        </div>
      )}
    </header>
  );
};
