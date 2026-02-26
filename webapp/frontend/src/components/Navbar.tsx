import { Image, Menu, Settings } from 'lucide-react';

interface NavbarProps {
    currentPage: string;
}

export function Navbar({ currentPage }: NavbarProps) {
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

    return (
        <nav className="h-16 border-b bg-card flex items-center justify-between px-6 shrink-0 z-40">
            <div className="flex items-center gap-3">
                <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-400">
                    {getTitle()}
                </h1>
            </div>

            <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 px-3 py-1.5 bg-secondary rounded-full text-sm">
                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-muted-foreground">System Online</span>
                </div>

                <button className="p-2 hover:bg-secondary rounded-full transition-colors text-muted-foreground hover:text-foreground">
                    <Settings className="w-5 h-5" />
                </button>
            </div>
        </nav>
    );
}
