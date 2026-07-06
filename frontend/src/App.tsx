import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import AICommandCenter from './pages/AICommandCenter';
import CityMap from './pages/CityMap';
import Analytics from './pages/Analytics';
import Reports from './pages/Reports';
import KnowledgeBase from './pages/KnowledgeBase';
import Settings from './pages/Settings';

function AppLayout() {
  const location = useLocation();
  const isMapPage = location.pathname === '/map';

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <main className={`flex-1 flex flex-col ${isMapPage ? "overflow-hidden" : "overflow-y-auto"}`}>
        <div className={isMapPage ? "flex-1 h-full relative p-6 flex flex-col min-h-0" : "max-w-[1400px] w-full mx-auto px-8 py-6"}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/ai-command" element={<AICommandCenter />} />
            <Route path="/map" element={<CityMap />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/knowledge-base" element={<KnowledgeBase />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
}

export default App;
