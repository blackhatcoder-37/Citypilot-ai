import { useEffect, useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, AreaChart, Area, BarChart, Bar,
} from 'recharts';
import {
  AlertCircle, Zap, ShieldAlert, CheckCircle2,
  TrendingUp, TrendingDown, ArrowUpRight, Clock,
  MapPin, AlertTriangle,
} from 'lucide-react';

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444'];

interface DashboardData {
  top_cards: { active_complaints: number; critical_areas: number; resources_available: number; today_ai_insights: number };
  charts: {
    complaint_trend: { day: string; complaints: number; resolved: number }[];
    risk_distribution: { name: string; value: number }[];
    weather_trend: { day: string; temp: number; rain: number }[];
    resource_usage: { name: string; used: number; available: number }[];
  };
  recent_incidents: { id: number; title: string; location: string; status: string; time: string; category: string }[];
  insights: string[];
}

const statusColor: Record<string, string> = {
  Critical: 'bg-danger/10 text-danger border-danger/20',
  High: 'bg-warning/10 text-warning border-warning/20',
  Medium: 'bg-info/10 text-info border-info/20',
  Low: 'bg-success/10 text-success border-success/20',
};

const Dashboard = () => {
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/dashboard')
      .then(res => res.json())
      .then(json => {
        if (json.success && json.data) {
          setData(json.data);
        }
      })
      .catch(err => console.error('Dashboard fetch error:', err));
  }, []);

  if (!data) return <DashboardSkeleton />;

  const topCards = [
    { title: 'Active Complaints', value: data.top_cards.active_complaints, icon: AlertCircle, color: 'text-warning', bg: 'bg-warning/10', trend: '+8%', trendUp: true },
    { title: 'Critical Areas', value: data.top_cards.critical_areas, icon: ShieldAlert, color: 'text-danger', bg: 'bg-danger/10', trend: '-1', trendUp: false },
    { title: 'Resources Available', value: `${data.top_cards.resources_available}%`, icon: CheckCircle2, color: 'text-success', bg: 'bg-success/10', trend: '+3%', trendUp: true },
    { title: "AI Insights Today", value: data.top_cards.today_ai_insights, icon: Zap, color: 'text-primary', bg: 'bg-primary/10', trend: '+5', trendUp: true },
  ];

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary tracking-tight">Dashboard</h1>
          <p className="text-sm text-text-muted mt-1">Real-time city operations overview</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-text-muted">
          <Clock size={14} />
          <span>Last updated: just now</span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {topCards.map((card, i) => (
          <div key={i} className={`glass rounded-xl p-5 hover:glass-hover transition-all duration-300 fade-in-delay-${i + 1}`}>
            <div className="flex items-center justify-between mb-3">
              <p className="text-xs font-medium text-text-muted uppercase tracking-wider">{card.title}</p>
              <div className={`w-8 h-8 rounded-lg ${card.bg} flex items-center justify-center`}>
                <card.icon size={16} className={card.color} />
              </div>
            </div>
            <div className="flex items-end justify-between">
              <h3 className="text-2xl font-bold text-text-primary">{card.value}</h3>
              <span className={`flex items-center gap-0.5 text-xs font-medium ${card.trendUp ? 'text-success' : 'text-danger'}`}>
                {card.trendUp ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                {card.trend}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="glass rounded-xl p-5 lg:col-span-2">
          <div className="flex items-center justify-between mb-5">
            <h3 className="text-sm font-semibold text-text-primary">Complaint Trend</h3>
            <span className="text-[10px] text-text-muted font-medium uppercase tracking-wider">Last 7 Days</span>
          </div>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.charts.complaint_trend}>
                <defs>
                  <linearGradient id="gradComplaints" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gradResolved" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="day" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#1a1f2e', borderColor: 'rgba(255,255,255,0.06)', borderRadius: 12, fontSize: 12 }} />
                <Area type="monotone" dataKey="complaints" stroke="#6366f1" strokeWidth={2} fill="url(#gradComplaints)" />
                <Area type="monotone" dataKey="resolved" stroke="#10b981" strokeWidth={2} fill="url(#gradResolved)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-semibold text-text-primary mb-5">Risk Distribution</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data.charts.risk_distribution} innerRadius={55} outerRadius={75} paddingAngle={4} dataKey="value" stroke="none">
                  {data.charts.risk_distribution.map((_entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1a1f2e', borderColor: 'rgba(255,255,255,0.06)', borderRadius: 12, fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-2">
            {data.charts.risk_distribution.map((item, i) => (
              <div key={item.name} className="flex items-center gap-2 text-xs text-text-secondary">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[i] }} />
                <span>{item.name}</span>
                <span className="ml-auto font-medium text-text-primary">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-semibold text-text-primary mb-5">Weather Forecast</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.charts.weather_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="day" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#1a1f2e', borderColor: 'rgba(255,255,255,0.06)', borderRadius: 12, fontSize: 12 }} />
                <Line type="monotone" dataKey="temp" stroke="#f59e0b" strokeWidth={2} dot={false} name="Temp (°C)" />
                <Line type="monotone" dataKey="rain" stroke="#3b82f6" strokeWidth={2} dot={false} name="Rain (mm)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-semibold text-text-primary mb-5">Resource Utilization</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.charts.resource_usage} layout="vertical" barSize={12}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
                <XAxis type="number" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis type="category" dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} width={90} />
                <Tooltip contentStyle={{ backgroundColor: '#1a1f2e', borderColor: 'rgba(255,255,255,0.06)', borderRadius: 12, fontSize: 12 }} />
                <Bar dataKey="used" stackId="a" fill="#6366f1" radius={[0, 0, 0, 0]} name="Deployed" />
                <Bar dataKey="available" stackId="a" fill="rgba(99,102,241,0.2)" radius={[0, 4, 4, 0]} name="Available" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        {/* Recent Incidents */}
        <div className="glass rounded-xl p-5 lg:col-span-3">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-text-primary">Recent Incidents</h3>
            <button className="text-xs text-primary-light hover:text-primary font-medium flex items-center gap-1 transition-colors">
              View all <ArrowUpRight size={12} />
            </button>
          </div>
          <div className="space-y-2">
            {data.recent_incidents.map((incident) => (
              <div key={incident.id} className="flex items-center gap-4 p-3 rounded-lg hover:bg-white/[0.02] transition-colors group">
                <div className="w-8 h-8 rounded-lg bg-white/[0.04] flex items-center justify-center shrink-0">
                  <AlertTriangle size={14} className="text-text-muted group-hover:text-warning transition-colors" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-text-primary truncate">{incident.title}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <MapPin size={10} className="text-text-muted" />
                    <span className="text-xs text-text-muted">{incident.location}</span>
                    <span className="text-xs text-text-muted">•</span>
                    <span className="text-xs text-text-muted">{incident.time}</span>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-md text-[10px] font-semibold border ${statusColor[incident.status] || 'bg-white/5 text-text-muted border-border'}`}>
                  {incident.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* AI Insights */}
        <div className="glass rounded-xl p-5 lg:col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-6 h-6 rounded-md bg-primary/10 flex items-center justify-center">
              <Zap size={12} className="text-primary" />
            </div>
            <h3 className="text-sm font-semibold text-text-primary">AI Insights</h3>
          </div>
          <div className="space-y-3">
            {data.insights.map((insight, i) => (
              <div key={i} className="p-3 rounded-lg bg-primary/[0.04] border border-primary/10 text-xs text-text-secondary leading-relaxed">
                {insight}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const DashboardSkeleton = () => (
  <div className="space-y-6">
    <div className="h-8 w-40 skeleton" />
    <div className="grid grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => <div key={i} className="h-24 skeleton" />)}
    </div>
    <div className="grid grid-cols-3 gap-4">
      <div className="h-72 col-span-2 skeleton" />
      <div className="h-72 skeleton" />
    </div>
  </div>
);

export default Dashboard;
