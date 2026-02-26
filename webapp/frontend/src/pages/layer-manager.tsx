import { Layers, Eye, EyeOff, Lock, Unlock, Plus, Trash2 } from 'lucide-react';

export default function LayerManager() {
    const layers = [
        { id: 1, name: 'Text Overlay', visible: true, locked: false, type: 'text' },
        { id: 2, name: 'Color Adjustment', visible: true, locked: true, type: 'adjust' },
        { id: 3, name: 'Background', visible: true, locked: true, type: 'image' },
    ];

    return (
        <div className="max-w-3xl mx-auto">
            <div className="mb-6 flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">Layer Management</h2>
                    <p className="text-muted-foreground">Advanced layer operations and organization</p>
                </div>
                <div className="flex gap-2">
                    <button className="bg-secondary hovering:bg-secondary/80 text-foreground px-3 py-2 rounded-md text-sm font-medium">Merge Down</button>
                    <button className="bg-primary text-primary-foreground px-3 py-2 rounded-md text-sm font-medium flex items-center gap-2">
                        <Plus className="w-4 h-4" /> New Layer
                    </button>
                </div>
            </div>

            <div className="bg-card rounded-xl border overflow-hidden">
                {layers.map((layer) => (
                    <div key={layer.id} className="flex items-center gap-4 p-4 border-b last:border-0 hover:bg-secondary/50 transition-colors">
                        <div className="flex items-center gap-2 text-muted-foreground">
                            <button className="hover:text-foreground">
                                {layer.visible ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                            </button>
                            <button className="hover:text-foreground">
                                {layer.locked ? <Lock className="w-4 h-4" /> : <Unlock className="w-4 h-4" />}
                            </button>
                        </div>

                        <div className="w-12 h-12 bg-secondary rounded border overflow-hidden flex items-center justify-center">
                            <Layers className="w-6 h-6 text-muted-foreground/50" />
                        </div>

                        <div className="flex-1">
                            <input
                                type="text"
                                defaultValue={layer.name}
                                className="bg-transparent font-medium focus:outline-none focus:underline"
                            />
                            <div className="text-xs text-muted-foreground capitalize">{layer.type} Layer</div>
                        </div>

                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2">
                                <span className="text-xs text-muted-foreground">Opacity</span>
                                <input type="range" className="w-24 accent-primary" defaultValue={100} />
                            </div>
                            <select className="bg-secondary border rounded text-xs p-1">
                                <option>Normal</option>
                                <option>Multiply</option>
                                <option>Screen</option>
                            </select>
                            <button className="text-muted-foreground hover:text-destructive transition-colors">
                                <Trash2 className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
