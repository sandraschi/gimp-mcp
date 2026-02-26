import { Terminal, Play, Save, Trash } from 'lucide-react';

export default function ScriptFuConsole() {
    return (
        <div className="h-full flex flex-col gap-4">
            <div className="flex items-center justify-between shrink-0">
                <div>
                    <h2 className="text-2xl font-bold">Script-Fu Console</h2>
                    <p className="text-muted-foreground">Execute Scheme scripts directly in GIMP</p>
                </div>
                <div className="flex gap-2">
                    <button className="bg-secondary hover:bg-secondary/80 p-2 rounded-md">
                        <Trash className="w-4 h-4" />
                    </button>
                    <button className="bg-secondary hover:bg-secondary/80 px-3 py-2 rounded-md text-sm font-medium flex items-center gap-2">
                        <Save className="w-4 h-4" /> Save
                    </button>
                    <button className="bg-primary text-primary-foreground px-3 py-2 rounded-md text-sm font-medium flex items-center gap-2">
                        <Play className="w-4 h-4" /> Run Script
                    </button>
                </div>
            </div>

            <div className="flex-1 bg-card rounded-xl border grid grid-rows-[1fr_auto] overflow-hidden">
                <div className="p-4 font-mono text-sm space-y-2 overflow-y-auto">
                    <div className="text-muted-foreground"># GIMP Script-Fu Console initialized</div>
                    <div className="text-muted-foreground"># Connected to GIMP 2.10.38</div>
                    <div><span className="text-green-500">➜</span> (gimp-image-list)</div>
                    <div className="text-blue-400">#&lt;Image 1 "Untitled"&gt;</div>
                    <div><span className="text-green-500">➜</span></div>
                </div>

                <div className="border-t p-4 bg-secondary/10">
                    <div className="flex gap-2">
                        <span className="text-green-500 font-mono">➜</span>
                        <input
                            type="text"
                            className="flex-1 bg-transparent font-mono focus:outline-none"
                            placeholder="(script-fu-command ...)"
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
