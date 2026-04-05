import { Settings, Zap, Terminal, AlertCircle } from 'lucide-react';
import type { GimpSystemStatus } from '../App';

interface NavbarProps {
    currentPage: string;
    systemStatus: GimpSystemStatus | null;
}

export function Navbar({ currentPage, systemStatus }: NavbarProps) {
    const getTitle = () => {
        switch (currentPage) {
            case 'image-editor': return 'Image Editor';
            case 'batch-processor': return 'Batch Processor';
            case 'layer-manager': return 'Layer Manager';
            case 'system-status': return 'System Status';
            case 'script-fu-console': return 'Script-Fu Console';
            default: return 'GIMP MCP';
        }
    };

    const getStatusInfo = () => {
        if (!systemStatus) return { label: 'Connecting...', color: 'bg-yellow-500', icon: <AlertCircle className="w-4 h-4 text-yellow-500" /> };
        
        const mode = systemStatus.live_mode?.mode;
        if (mode === 'live') {
            return { label: 'Bridge: Live', color: 'bg-green-500', icon: <Zap className="w-4 h-4 text-green-500" /> };
        } else if (mode === 'headless') {
            return { label: 'Bridge: Headless', color: 'bg-blue-500', icon: <Terminal className="w-4 h-4 text-blue-500" /> };
        } else {
            return { label: 'Offline', color: 'bg-red-500', icon: <AlertCircle className="w-4 h-4 text-red-500" /> };
        }
    };

    const status = getStatusInfo();

    return (
        <nav className="h-16 border-b bg-card flex items-center justify-between px-6 shrink-0 z-40">
            <div className="flex items-center gap-3">
                <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-400">
                    {getTitle()}
                </h1>
            </div>

            <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 px-3 py-1.5 bg-secondary rounded-full text-sm">
                    <span className={`w-2 h-2 rounded-full ${status.color} ${systemStatus ? 'animate-pulse' : ''}`} />
                    <span className="text-foreground font-medium flex items-center gap-1.5">
                        {status.label}
                    </span>
                </div>

                <button 
                    className="p-2 hover:bg-secondary rounded-full transition-colors text-muted-foreground hover:text-foreground"
                    title="Settings"
                >
                    <Settings className="w-5 h-5" />
                </button>
            </div>
        </nav>
    );
}
