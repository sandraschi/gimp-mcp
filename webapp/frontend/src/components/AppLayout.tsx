import React from 'react';
import { Sidebar } from './Sidebar';
import { Navbar } from './Navbar';
import type { GimpSystemStatus } from '../App';

interface AppLayoutProps {
  children: React.ReactNode;
  currentPage: string;
  onNavigate: (page: string) => void;
  systemStatus: GimpSystemStatus | null;
}

export function AppLayout({ children, currentPage, onNavigate, systemStatus }: AppLayoutProps) {
  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans selection:bg-primary/30">
      <Sidebar currentPage={currentPage} onNavigate={onNavigate} />
      
      <div className="flex-1 flex flex-col min-w-0 bg-gradient-to-br from-background to-secondary/30">
        <Navbar currentPage={currentPage} systemStatus={systemStatus} />
        
        <main className="flex-1 overflow-y-auto p-8 relative scrollbar-thin scrollbar-thumb-primary/20 scrollbar-track-transparent hover:scrollbar-thumb-primary/30 transition-all">
          <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {children}
          </div>
          
          {/* Subtle background glow */}
          <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[120px] -z-10 pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-[300px] h-[300px] bg-purple-500/5 rounded-full blur-[100px] -z-10 pointer-events-none" />
        </main>
      </div>
    </div>
  );
}
