import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, BrainCircuit, BarChart3, Map as MapIcon,
  FileText, BookOpen, Settings, ChevronRight,
} from 'lucide-react';

const menuItems = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'AI Command Center', path: '/ai-command', icon: BrainCircuit },
  { name: 'Analytics', path: '/analytics', icon: BarChart3 },
  { name: 'City Map', path: '/map', icon: MapIcon },
  { name: 'Reports', path: '/reports', icon: FileText },
  { name: 'Knowledge Base', path: '/knowledge-base', icon: BookOpen },
  { name: 'Settings', path: '/settings', icon: Settings },
];

const Sidebar = () => {
  const location = useLocation();

  return (
    <aside className="w-[260px] min-w-[260px] h-screen flex flex-col border-r border-border bg-surface">
      {/* Logo */}
      <div className="px-6 py-6 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-primary/20 flex items-center justify-center">
            <BrainCircuit className="text-primary" size={20} />
          </div>
          <div>
            <h1 className="text-[15px] font-semibold text-text-primary tracking-tight">CityPilot AI</h1>
            <p className="text-[10px] text-text-muted font-medium tracking-wider uppercase">Decision Intelligence</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <p className="px-3 mb-3 text-[10px] font-semibold text-text-muted tracking-widest uppercase">Platform</p>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <NavLink
              key={item.name}
              to={item.path}
              className={`group flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13px] font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-primary/10 text-primary-light'
                  : 'text-text-secondary hover:text-text-primary hover:bg-white/[0.03]'
              }`}
            >
              <item.icon size={18} strokeWidth={isActive ? 2 : 1.5} />
              <span className="flex-1">{item.name}</span>
              {isActive && <ChevronRight size={14} className="opacity-50" />}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-border">
        <div className="flex items-center gap-3 px-2">
          <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-xs font-bold text-primary">
            CP
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-text-primary truncate">City Admin</p>
            <p className="text-[10px] text-text-muted">Commissioner</p>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
