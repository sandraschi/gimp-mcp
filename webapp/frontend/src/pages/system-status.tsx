import { Activity, CheckCircle2, AlertCircle, HardDrive, MemoryStick } from 'lucide-react';

export default function SystemStatus() {
    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <div>
                <h2 className="text-2xl font-bold">System Status</h2>
                <p className="text-muted-foreground">Monitor GIMP server performance and connections</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-card p-6 rounded-xl border space-y-2">
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-muted-foreground">Server Status</span>
                        <Activity className="w-4 h-4 text-green-500" />
                    </div>
                    <div className="text-2xl font-bold">Online</div>
                    <p className="text-xs text-muted-foreground">Uptime: 3d 4h 12m</p>
                </div>

                <div className="bg-card p-6 rounded-xl border space-y-2">
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-muted-foreground">Memory Usage</span>
                        <MemoryStick className="w-4 h-4 text-primary" />
                    </div>
                    <div className="text-2xl font-bold">1.2 GB</div>
                    <div className="w-full bg-secondary h-1.5 rounded-full overflow-hidden">
                        <div className="bg-primary h-full w-[45%]" />
                    </div>
                </div>

                <div className="bg-card p-6 rounded-xl border space-y-2">
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-muted-foreground">Disk Cache</span>
                        <HardDrive className="w-4 h-4 text-blue-500" />
                    </div>
                    <div className="text-2xl font-bold">4.8 GB</div>
                    <p className="text-xs text-muted-foreground">Max: 10 GB</p>
                </div>
            </div>

            <div className="bg-card rounded-xl border p-6">
                <h3 className="font-semibold mb-4">Diagnostics</h3>
                <div className="space-y-4">
                    {[
                        { label: 'GIMP Connection', status: 'connected', msg: 'Version 2.10.38 found' },
                        { label: 'FastMCP Transport', status: 'connected', msg: 'HTTP Streamable active' },
                        { label: 'Plugin System', status: 'warning', msg: '2 plugins failed to load' },
                        { label: 'Script-Fu Interface', status: 'connected', msg: 'Ready' },
                    ].map((item, i) => (
                        <div key={i} className="flex items-center justify-between py-2 border-b last:border-0">
                            <div className="flex items-center gap-3">
                                {item.status === 'connected' ? (
                                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                                ) : (
                                    <AlertCircle className="w-5 h-5 text-yellow-500" />
                                )}
                                <span className="font-medium">{item.label}</span>
                            </div>
                            <span className="text-sm text-muted-foreground">{item.msg}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
