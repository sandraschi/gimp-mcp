import { useState } from 'react';
import { Upload, Sliders, Eraser, Move, Crop, Type, Layers, Wand2 } from 'lucide-react';

export default function ImageEditor() {
    const [activeTool, setActiveTool] = useState('move');

    const tools = [
        { id: 'move', icon: Move, label: 'Move' },
        { id: 'crop', icon: Crop, label: 'Crop' },
        { id: 'wand', icon: Wand2, label: 'Select' },
        { id: 'type', icon: Type, label: 'Text' },
        { id: 'eraser', icon: Eraser, label: 'Eraser' },
    ];

    return (
        <div className="flex h-full gap-4">
            {/* Tools Panel */}
            <div className="w-16 bg-card rounded-xl border flex flex-col items-center py-4 gap-4">
                {tools.map((tool) => (
                    <button
                        key={tool.id}
                        onClick={() => setActiveTool(tool.id)}
                        className={`p-3 rounded-lg transition-colors ${activeTool === tool.id
                                ? 'bg-primary text-primary-foreground'
                                : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                            }`}
                        title={tool.label}
                    >
                        <tool.icon className="w-5 h-5" />
                    </button>
                ))}
                <div className="h-px w-8 bg-border my-2" />
                <button className="p-3 rounded-lg text-muted-foreground hover:bg-secondary hover:text-foreground">
                    <Sliders className="w-5 h-5" />
                </button>
            </div>

            {/* Main Canvas Area */}
            <div className="flex-1 bg-secondary/30 rounded-xl border border-dashed border-border flex items-center justify-center relative overflow-hidden group">
                <div className="text-center p-8 transition-opacity group-hover:opacity-50">
                    <Upload className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-medium">No Image Loaded</h3>
                    <p className="text-sm text-muted-foreground mt-1">Drag and drop or click to upload</p>
                    <button className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
                        Open Image
                    </button>
                </div>
            </div>

            {/* Properties Panel */}
            <div className="w-72 bg-card rounded-xl border p-4">
                <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <Layers className="w-4 h-4" />
                    Properties
                </h3>

                <div className="space-y-6">
                    <div className="space-y-2">
                        <label className="text-xs font-medium text-muted-foreground">Opacity</label>
                        <input type="range" className="w-full accent-primary" />
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs font-medium text-muted-foreground">Blend Mode</label>
                        <select className="w-full bg-secondary border rounded-md p-2 text-sm">
                            <option>Normal</option>
                            <option>Multiply</option>
                            <option>Screen</option>
                            <option>Overlay</option>
                        </select>
                    </div>

                    <div className="p-4 bg-secondary/50 rounded-lg">
                        <p className="text-xs text-muted-foreground text-center">Select a layer to view properties</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
