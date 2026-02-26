import {
    Image,
    Layers,
    Terminal,
    Activity,
    Copy,
    Wand2
} from 'lucide-react';
import clsx from 'clsx';

interface SidebarProps {
    currentPage: string;
    onNavigate: (page: string) => void;
}

export function Sidebar({ currentPage, onNavigate }: SidebarProps) {
    const navItems = [
        { id: 'image-editor', icon: Image, label: 'Editor' },
        { id: 'batch-processor', icon: Copy, label: 'Batch' },
        { id: 'layer-manager', icon: Layers, label: 'Layers' },
        { id: 'system-status', icon: Activity, label: 'Status' },
        { id: 'script-fu-console', icon: Terminal, label: 'Script-Fu' },
    ];

    return (
        <aside className="w-64 bg-card border-r flex flex-col shrink-0 z-50">
            <div className="h-16 flex items-center px-6 border-b shrink-0">
                <div className="flex items-center gap-2 font-bold text-xl">
                    <Wand2 className="w-6 h-6 text-primary" />
                    <span>GIMP MCP</span>
                </div>
            </div>

            <div className="p-4 flex flex-col gap-2 overflow-y-auto flex-1">
                {navItems.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => onNavigate(item.id)}
                        className={clsx(
                            "flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200",
                            currentPage === item.id
                                ? "bg-primary/10 text-primary hover:bg-primary/15"
                                : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                        )}
                    >
                        <item.icon className="w-5 h-5" />
                        {item.label}
                    </button>
                ))}
            </div>

            <div className="p-4 border-t shrink-0">
                <div className="bg-secondary/50 rounded-lg p-3">
                    <p className="text-xs font-medium text-muted-foreground mb-1">GIMP Connection</p>
                    <div className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                        <span className="text-xs">Connected (v2.10.38)</span>
                    </div>
                </div>
            </div>
        </aside>
    );
}
