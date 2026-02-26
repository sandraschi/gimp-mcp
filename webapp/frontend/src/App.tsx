import { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import ImageEditor from './pages/image-editor';
import BatchProcessor from './pages/batch-processor';
import LayerManager from './pages/layer-manager';
import SystemStatus from './pages/system-status';
import ScriptFuConsole from './pages/script-fu-console';

function App() {
  const [currentPage, setCurrentPage] = useState('image-editor');

  const renderPage = () => {
    switch (currentPage) {
      case 'image-editor':
        return <ImageEditor />;
      case 'batch-processor':
        return <BatchProcessor />;
      case 'layer-manager':
        return <LayerManager />;
      case 'system-status':
        return <SystemStatus />;
      case 'script-fu-console':
        return <ScriptFuConsole />;
      default:
        return <ImageEditor />;
    }
  };

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      <Sidebar currentPage={currentPage} onNavigate={setCurrentPage} />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar currentPage={currentPage} />
        <main className="flex-1 overflow-auto p-6 scrollbar-thin scrollbar-thumb-accent scrollbar-track-transparent">
          {renderPage()}
        </main>
      </div>
    </div>
  );
}

export default App;
