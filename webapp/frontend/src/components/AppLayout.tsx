import type React from "react";
import { HelpModal } from "./HelpModal";
import { LoggerModal } from "./LoggerModal";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";

interface AppLayoutProps {
  children: React.ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans selection:bg-primary/30">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0 bg-gradient-to-br from-background to-secondary/30">
        <Navbar />

        <main className="flex-1 overflow-y-auto p-6 relative">
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
            {children}
          </div>

          <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[120px] -z-10 pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-[300px] h-[300px] bg-purple-500/5 rounded-full blur-[100px] -z-10 pointer-events-none" />
        </main>
      </div>

      <LoggerModal />
      <HelpModal />
    </div>
  );
}
