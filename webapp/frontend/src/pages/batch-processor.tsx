import { Play, Plus, Trash2, FileImage } from 'lucide-react';

export default function BatchProcessor() {
    return (
        <div className="max-w-5xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">Batch Processing</h2>
                    <p className="text-muted-foreground">Apply operations to multiple images simultaneously</p>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
                    <Play className="w-4 h-4" />
                    Start Processing
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Input Files */}
                <div className="bg-card rounded-xl border p-6 space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="font-semibold">Input Files</h3>
                        <button className="text-sm text-primary hover:underline flex items-center gap-1">
                            <Plus className="w-3 h-3" /> Add Files
                        </button>
                    </div>

                    <div className="bg-secondary/30 border border-dashed rounded-lg p-8 text-center">
                        <FileImage className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                        <p className="text-sm text-muted-foreground">Drop files here to process</p>
                    </div>
                </div>

                {/* Operations Pipeline */}
                <div className="bg-card rounded-xl border p-6 space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="font-semibold">Operations Pipeline</h3>
                        <button className="text-sm text-primary hover:underline flex items-center gap-1">
                            <Plus className="w-3 h-3" /> Add Operation
                        </button>
                    </div>

                    <div className="space-y-3">
                        {[
                            { name: 'Resize', detail: '1920x1080 (Maintain Aspect)' },
                            { name: 'Color Correction', detail: 'Auto Levels' },
                            { name: 'Watermark', detail: 'Bottom Right, 50% Opacity' },
                            { name: 'Export', detail: 'JPG, 85% Quality' },
                        ].map((op, i) => (
                            <div key={i} className="flex items-center justify-between p-3 bg-secondary rounded-lg border border-transparent hover:border-primary/50 transition-colors group">
                                <div>
                                    <div className="font-medium text-sm">{op.name}</div>
                                    <div className="text-xs text-muted-foreground">{op.detail}</div>
                                </div>
                                <button className="opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/10 hover:text-destructive rounded transition-all">
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
