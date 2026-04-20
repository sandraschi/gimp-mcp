import { useState, useEffect } from 'react';
import { AppLayout } from './components/AppLayout';
import ImageEditor from './pages/image-editor';
import BatchProcessor from './pages/batch-processor';
import LayerManager from './pages/layer-manager';
import SystemStatus from './pages/system-status';
import ScriptFuConsole from './pages/script-fu-console';
import ToolsExplorer from './pages/ToolsExplorer';
import FastmcpSotaPage from './pages/fastmcp-sota';

export interface GimpSystemStatus {
  status: string;
  live_mode: {
    mode: 'live' | 'headless' | 'offline';
    last_check?: string;
    details?: string;
  };
  config?: {
    gimp_executable: string;
    max_concurrent_processes: number;
  };
  server_name?: string;
  version?: string;
  fastmcp?: string;
  sota?: {
    package?: string;
    fastmcp?: string;
    sota_target?: string;
    features?: Record<string, unknown>;
  };
}

function App() {
  const [currentPage, setCurrentPage] = useState('image-editor');
  const [systemStatus, setSystemStatus] = useState<GimpSystemStatus | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('/api/health');
        if (response.ok) {
          const data = await response.json();
          setSystemStatus(data);
        }
      } catch (error) {
        console.error('Failed to fetch system status:', error);
        setSystemStatus(prev => prev ? { ...prev, status: 'unreachable' } : null);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case 'image-editor':
        return <ImageEditor />;
      case 'batch-processor':
        return <BatchProcessor />;
      case 'layer-manager':
        return <LayerManager />;
      case 'tools-explorer':
        return <ToolsExplorer />;
      case 'system-status':
        return <SystemStatus status={systemStatus} />;
      case 'script-fu-console':
        return <ScriptFuConsole />;
      case 'fastmcp-sota':
        return <FastmcpSotaPage />;
      default:
        return <ImageEditor />;
    }
  };

  return (
    <AppLayout 
      currentPage={currentPage} 
      onNavigate={setCurrentPage}
      systemStatus={systemStatus}
    >
      {renderPage()}
    </AppLayout>
  );
}

export default App;
