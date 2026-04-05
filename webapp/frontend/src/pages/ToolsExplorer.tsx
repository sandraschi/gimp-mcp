import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Badge } from '../components/ui-core';
import { Search, Terminal, Box, Filter, Sliders, Layers, Activity, Copy } from 'lucide-react';

interface Tool {
  name: string;
  description: string;
  inputSchema: any;
}

export default function ToolsExplorer() {
  const [tools, setTools] = useState<Tool[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchTools() {
      try {
        const response = await fetch('/api/tools');
        const data = await response.json();
        setTools(data.tools || []);
      } catch (error) {
        console.error('Failed to fetch tools:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchTools();
  }, []);

  const filteredTools = tools.filter(tool => 
    tool.name.toLowerCase().includes(search.toLowerCase()) ||
    tool.description.toLowerCase().includes(search.toLowerCase())
  );

  const getCategoryIcon = (name: string) => {
    if (name.includes('file')) return <Box className="w-4 h-4" />;
    if (name.includes('transform')) return <Sliders className="w-4 h-4" />;
    if (name.includes('color')) return <Filter className="w-4 h-4" />;
    if (name.includes('layer')) return <Layers className="w-4 h-4" />;
    if (name.includes('filter')) return <Terminal className="w-4 h-4" />;
    if (name.includes('batch')) return <Copy className="w-4 h-4" />;
    if (name.includes('system')) return <Activity className="w-4 h-4" />;
    return <Terminal className="w-4 h-4" />;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Tools Explorer</h2>
          <p className="text-muted-foreground mt-1">
            Browse and inspect all registered portmanteau tools for GIMP MCP.
          </p>
        </div>
        
        <div className="relative w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search tools..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-secondary border-none rounded-xl focus:ring-2 focus:ring-primary/50 transition-all outline-none"
          />
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="h-48 bg-card/50 animate-pulse rounded-2xl" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTools.map((tool) => (
            <Card key={tool.name} className="group hover:shadow-xl hover:shadow-primary/5 transition-all duration-300 border-primary/5 hover:border-primary/20 bg-card/80 backdrop-blur-sm overflow-hidden">
              <CardHeader className="pb-3 px-6 pt-6">
                <div className="flex items-center justify-between mb-2">
                  <div className="p-2 bg-primary/10 rounded-lg group-hover:bg-primary/20 transition-colors">
                    {getCategoryIcon(tool.name)}
                  </div>
                  <Badge variant="secondary" className="font-mono text-[10px] uppercase">3.1 SOTA</Badge>
                </div>
                <CardTitle className="text-lg font-bold group-hover:text-primary transition-colors">
                  {tool.name}
                </CardTitle>
                <CardDescription className="line-clamp-2 text-xs leading-relaxed">
                  {tool.description}
                </CardDescription>
              </CardHeader>
              <CardContent className="px-6 pb-6 pt-0">
                <div className="pt-4 border-t border-primary/5 flex items-center justify-between">
                  <div className="flex gap-1">
                    {Object.keys(tool.inputSchema?.properties || {}).slice(0, 3).map(prop => (
                      <span key={prop} className="text-[10px] px-1.5 py-0.5 bg-secondary text-muted-foreground rounded">
                        {prop}
                      </span>
                    ))}
                  </div>
                  <span className="text-[10px] text-muted-foreground font-mono">
                    {Object.keys(tool.inputSchema?.properties || {}).length} params
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
