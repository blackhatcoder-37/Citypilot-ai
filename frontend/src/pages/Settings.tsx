import { useEffect, useState } from 'react';
import { Settings as SettingsIcon, User, Bell, Shield, Database } from 'lucide-react';

interface SystemStatus {
  api_status: string;
  database_type: string;
  database_status: string;
  database_version: string;
  connection_pool_size: number;
  ai_engine: string;
  app_version: string;
}

const Settings = () => {
  const [system, setSystem] = useState<SystemStatus | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/settings')
      .then(res => res.json())
      .then(json => {
        if (json.success && json.data) setSystem(json.data);
      })
      .catch(() => {
        // Fallback if API is unreachable
        setSystem({
          api_status: 'Disconnected',
          database_type: 'PostgreSQL',
          database_status: 'Unknown',
          database_version: 'Unknown',
          connection_pool_size: 0,
          ai_engine: 'Gemini — Placeholder',
          app_version: 'v1.0.0-beta',
        });
      });
  }, []);

  const systemRows: [string, string, string][] = system
    ? [
        ['API Status', system.api_status, system.api_status === 'Connected' ? 'text-success' : 'text-danger'],
        ['Database', `${system.database_type} — ${system.database_status}`, system.database_status === 'Healthy' ? 'text-success' : 'text-warning'],
        ['DB Version', system.database_version, 'text-text-secondary'],
        ['Connection Pool', `${system.connection_pool_size} connections`, 'text-text-secondary'],
        ['AI Engine', system.ai_engine, 'text-warning'],
        ['Version', system.app_version, 'text-text-secondary'],
      ]
    : [
        ['API Status', 'Loading...', 'text-text-muted'],
        ['Database', 'Loading...', 'text-text-muted'],
      ];

  return (
    <div className="space-y-6 fade-in max-w-3xl">
      <div>
        <h1 className="text-2xl font-semibold text-text-primary tracking-tight flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-primary/20 flex items-center justify-center">
            <SettingsIcon size={20} className="text-primary" />
          </div>
          Settings
        </h1>
        <p className="text-sm text-text-muted mt-2 ml-12">Configure platform preferences and system parameters</p>
      </div>

      {/* Profile */}
      <div className="glass rounded-xl p-5">
        <div className="flex items-center gap-3 mb-5">
          <User size={16} className="text-text-muted" />
          <h3 className="text-sm font-semibold text-text-primary">Profile</h3>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-text-muted mb-1.5 block">Full Name</label>
            <input type="text" defaultValue="Commissioner Mehta" className="w-full bg-white/[0.03] border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary/40" />
          </div>
          <div>
            <label className="text-xs text-text-muted mb-1.5 block">Role</label>
            <input type="text" defaultValue="City Commissioner" disabled className="w-full bg-white/[0.02] border border-border rounded-lg px-3 py-2 text-sm text-text-muted" />
          </div>
          <div>
            <label className="text-xs text-text-muted mb-1.5 block">Email</label>
            <input type="email" defaultValue="commissioner@citypilot.gov" className="w-full bg-white/[0.03] border border-border rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-primary/40" />
          </div>
          <div>
            <label className="text-xs text-text-muted mb-1.5 block">Department</label>
            <input type="text" defaultValue="Municipal Corporation" disabled className="w-full bg-white/[0.02] border border-border rounded-lg px-3 py-2 text-sm text-text-muted" />
          </div>
        </div>
      </div>

      {/* Notifications */}
      <div className="glass rounded-xl p-5">
        <div className="flex items-center gap-3 mb-5">
          <Bell size={16} className="text-text-muted" />
          <h3 className="text-sm font-semibold text-text-primary">Notifications</h3>
        </div>
        <div className="space-y-4">
          {['Critical Risk Alerts', 'Daily Morning Brief', 'Resource Deployment Updates', 'AI Prediction Reports'].map((item) => (
            <div key={item} className="flex items-center justify-between py-1">
              <span className="text-sm text-text-secondary">{item}</span>
              <button className="w-10 h-5 rounded-full bg-primary/30 relative transition-colors">
                <div className="w-4 h-4 rounded-full bg-primary absolute right-0.5 top-0.5 transition-transform" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* System */}
      <div className="glass rounded-xl p-5">
        <div className="flex items-center gap-3 mb-5">
          <Database size={16} className="text-text-muted" />
          <h3 className="text-sm font-semibold text-text-primary">System</h3>
        </div>
        <div className="space-y-3 text-xs">
          {systemRows.map(([label, value, color]) => (
            <div key={label} className="flex justify-between py-2 border-b border-border">
              <span className="text-text-muted">{label}</span>
              <span className={`font-medium ${color}`}>{value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Security */}
      <div className="glass rounded-xl p-5">
        <div className="flex items-center gap-3 mb-5">
          <Shield size={16} className="text-text-muted" />
          <h3 className="text-sm font-semibold text-text-primary">Security</h3>
        </div>
        <button className="px-4 py-2 rounded-lg bg-white/[0.04] border border-border text-xs text-text-secondary hover:text-text-primary hover:border-border-hover transition-all">
          Change Password
        </button>
      </div>
    </div>
  );
};

export default Settings;
