import React from 'react';
import {
  ShieldAlert,
  RotateCcw,
  LayoutDashboard,
  AlertTriangle,
  History,
  Sparkles,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { MemoryStatus } from '../types';

interface NavbarProps {
  currentTab: 'dashboard' | 'incidents' | 'investigate' | 'timeline';
  setCurrentTab: (tab: 'dashboard' | 'incidents' | 'investigate' | 'timeline') => void;
  memoryStatus: MemoryStatus | null;
  onResetDemo: () => void;
  isResetting: boolean;
  demoMode: boolean;
  setDemoMode: (val: boolean) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  setCurrentTab,
  memoryStatus,
  onResetDemo,
  isResetting,
  demoMode,
  setDemoMode,
}) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50 px-6 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentTab('dashboard')}>
          <div className="p-2 bg-indigo-600/20 text-indigo-400 rounded-lg border border-indigo-500/30 shadow-inner">
            <ShieldAlert className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-base font-bold tracking-tight text-white">Incident Response Agent</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-700/50">
                PROD v1.0
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              An AI agent that remembers how your organization solved problems before.
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 bg-slate-950/70 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setCurrentTab('dashboard')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              currentTab === 'dashboard'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>Dashboard</span>
          </button>

          <button
            onClick={() => setCurrentTab('incidents')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              currentTab === 'incidents' || currentTab === 'investigate'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Incidents</span>
          </button>

          <button
            onClick={() => setCurrentTab('timeline')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              currentTab === 'timeline'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <History className="w-3.5 h-3.5" />
            <span>Memory Audit</span>
          </button>
        </nav>

        {/* Actions & Hindsight Status */}
        <div className="flex items-center space-x-3">
          {/* Guided Story Toggle */}
          <button
            onClick={() => setDemoMode(!demoMode)}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium border transition-all ${
              demoMode
                ? 'bg-purple-950/90 text-purple-200 border-purple-600/80 shadow-sm'
                : 'bg-slate-800/60 text-slate-300 border-slate-700 hover:bg-slate-700/60'
            }`}
            title="Toggle Guided 3-Incident Learning Story"
          >
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            <span className="hidden md:inline">Guided Demo Flow</span>
          </button>

          {/* Reset Demo Button */}
          <button
            onClick={onResetDemo}
            disabled={isResetting}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium bg-slate-800/60 hover:bg-rose-950/40 text-slate-300 hover:text-rose-300 border border-slate-700 hover:border-rose-700/50 transition-all disabled:opacity-50"
            title="Reset demo incidents to clean un-retained state"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${isResetting ? 'animate-spin text-rose-400' : 'text-slate-400'}`} />
            <span className="hidden md:inline">{isResetting ? 'Resetting...' : 'Reset Demo'}</span>
          </button>

          {/* Real Hindsight Status Pill */}
          <div
            className={`flex items-center space-x-2 text-xs px-3 py-1.5 rounded-full border shadow-sm ${
              memoryStatus === null
                ? 'bg-slate-800/60 border-slate-700 text-slate-300'
                : memoryStatus.connected
                ? 'bg-emerald-950/60 border-emerald-600/50 text-emerald-300'
                : 'bg-rose-950/60 border-rose-600/50 text-rose-300'
            }`}
            title={`Bank: ${memoryStatus?.bank_id || 'incident-response-bank'} @ ${memoryStatus?.hindsight_base_url || '127.0.0.1:8888'}`}
          >
            {memoryStatus === null ? (
              <RotateCcw className="w-3.5 h-3.5 text-slate-400 animate-spin" />
            ) : memoryStatus.connected ? (
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            ) : (
              <XCircle className="w-3.5 h-3.5 text-rose-400" />
            )}
            <div className="flex items-center gap-1">
              <span className="font-semibold">Hindsight:</span>
              <span className="font-mono text-[11px]">
                {memoryStatus === null
                  ? 'CHECKING...'
                  : memoryStatus.connected
                  ? 'CONNECTED'
                  : 'DISCONNECTED'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
