import { Activity, CheckCircle2, AlertCircle, Zap, Terminal, Server } from 'lucide-react';
import type { GimpSystemStatus } from '../App';

interface SystemStatusProps {
    status: GimpSystemStatus | null;
}

export default function SystemStatus({ status }: SystemStatusProps) {
    const getModeIcon = (mode: string) => {
        switch (mode) {
            case 'live': return <Zap className="w-4 h-4 text-green-500" />;
            case 'headless': return <Terminal className="w-4 h-4 text-blue-500" />;
            default: return <Activity className="w-4 h-4 text-red-500" />;
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-2xl font-bold">System Status</h2>
                    <p className="text-muted-foreground">Monitor GIMP server performance and connections</p>
                </div>
                {status?.version && (
                    <span className="px-2 py-1 bg-secondary rounded text-xs text-muted-foreground">
                        v{status.version}
                    </span>
                )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-card p-6 rounded-xl border border-border/50 bg-gradient-to-br from-card to-secondary/10 space-y-2">
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-muted-foreground">Connection Mode</span>
                        {getModeIcon(status?.live_mode?.mode || 'offline')}
                    </div>
                    <div className="text-2xl font-bold capitalize">
                        {status?.live_mode?.mode || 'Offline'}
                    </div>
                    <p className="text-xs text-muted-foreground">
                        Bridge: {status?.live_mode?.mode === 'live' ? 'Connected' : 'Fallback/Legacy'}
                    </p>
                </div>

                <div className="bg-card p-6 rounded-xl border border-border/50 bg-gradient-to-br from-card to-secondary/10 space-y-2">
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-muted-foreground">Endpoint Status</span>
                        <Server className="w-4 h-4 text-primary" />
                    </div>
                    <div className="text-2xl font-bold capitalize">
                        {status?.status || 'Unknown'}
                    </div>
                    <div className="w-full bg-secondary h-1.5 rounded-full overflow-hidden">
                        <div className={`h-full ${status?.status === 'healthy' ? 'bg-green-500 w-full' : 'bg-red-500 w-[10%]'}`} />
                    </div>
                </div>

                <div className="bg-card p-6 rounded-xl border border-border/50 bg-gradient-to-br from-card to-secondary/10 space-y-2">
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-muted-foreground">Command Queue</span>
                        <Activity className="w-4 h-4 text-blue-500" />
                    </div>
                    <div className="text-2xl font-bold">Ready</div>
                    <p className="text-xs text-muted-foreground">Max Concurrent: {status?.config?.max_concurrent_processes || 4}</p>
                </div>
            </div>

            <div className="bg-card rounded-xl border border-border/50 p-6">
                <h3 className="font-semibold mb-4">Diagnostics</h3>
                <div className="space-y-4">
                    {[
                        { 
                            label: 'GIMP Connectivity', 
                            status: status?.live_mode?.mode !== 'offline' ? 'connected' : 'error', 
                            msg: status?.live_mode?.details || 'GIMP bridge unreachable' 
                        },
                        { 
                            label: 'FastMCP Transport', 
                            status: 'connected', 
                            msg: `HTTP Streamable — FastMCP 3.2 (${status?.fastmcp ? String(status.fastmcp) : 'see /api/sota'})` 
                        },
                        { 
                            label: 'Binary Path', 
                            status: 'connected', 
                            msg: status?.config?.gimp_executable || 'Autodetected' 
                        },
                        { 
                            label: 'Last Telemetry', 
                            status: 'connected', 
                            msg: status?.live_mode?.last_check || 'Just now' 
                        },
                    ].map((item, i) => (
                        <div key={i} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0 hover:bg-secondary/20 px-2 -mx-2 rounded transition-colors">
                            <div className="flex items-center gap-3">
                                {item.status === 'connected' ? (
                                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                                ) : (
                                    <AlertCircle className="w-5 h-5 text-red-500" />
                                )}
                                <span className="font-medium">{item.label}</span>
                            </div>
                            <span className="text-sm text-muted-foreground font-mono">{item.msg}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
