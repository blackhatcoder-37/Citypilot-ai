import { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, Radar, AreaChart, Area, LineChart, Line,
} from 'recharts';
import { TrendingUp, BarChart3 } from 'lucide-react';

const tooltipStyle = { backgroundColor: '#1a1f2e', borderColor: 'rgba(255,255,255,0.06)', borderRadius: 12, fontSize: 12 };

interface AnalyticsData {
  complaint_trend: Record<string, unknown>[];
  weekly_comparison: { day: string; thisWeek: number; lastWeek: number }[];
  department_performance: { subject: string; score: number; fullMark: number }[];
  prediction_timeline: { time: string; predicted: number; actual: number }[];
  resource_utilization: { name: string; utilized: number; target: number }[];
  status_distribution: { name: string; count: number }[];
}

const Analytics = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/analytics')
      .then(res => res.json())
      .then(json => {
        if (json.success && json.data) {
          setData(json.data);
        }
      })
      .catch(err => console.error('Analytics fetch error:', err));
  }, []);

  if (!data) return <div className="space-y-6"><div className="h-8 w-60 skeleton" /><div className="grid grid-cols-2 gap-4">{[...Array(6)].map((_, i) => <div key={i} className="h-72 skeleton" />)}</div></div>;

  // Derive category keys from complaint_trend data (exclude "name")
  const categoryKeys = data.complaint_trend.length > 0
    ? Object.keys(data.complaint_trend[0]).filter(k => k !== 'name')
    : ['Water_Leakage', 'Traffic', 'Power_Outage', 'Sewage'];

  const categoryColors: Record<string, string> = {
    Flood: '#3b82f6', Water_Leakage: '#3b82f6', Traffic: '#f59e0b',
    Power_Outage: '#ef4444', Sewage: '#6366f1', Garbage: '#10b981',
    Street_Light: '#eab308', Road_Damage: '#f97316', Medical_Emergency: '#ec4899',
  };

  // Compute weekly change %
  const thisWeekTotal = data.weekly_comparison.reduce((s, d) => s + d.thisWeek, 0);
  const lastWeekTotal = data.weekly_comparison.reduce((s, d) => s + d.lastWeek, 0);
  const weeklyChange = lastWeekTotal > 0 ? Math.round(((thisWeekTotal - lastWeekTotal) / lastWeekTotal) * 100) : 0;

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary tracking-tight flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-primary/20 flex items-center justify-center">
              <BarChart3 size={20} className="text-primary" />
            </div>
            City Analytics
          </h1>
          <p className="text-sm text-text-muted mt-2 ml-12">Comprehensive operational intelligence and trend analysis</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Complaint Trend */}
        <div className="glass rounded-xl p-5">
          <div className="flex items-center justify-between mb-5">
            <h3 className="text-sm font-semibold text-text-primary">Complaint Volumes by Category</h3>
            <span className="text-[10px] text-text-muted font-medium uppercase tracking-wider">6 Months</span>
          </div>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.complaint_trend} barGap={2}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend iconType="circle" iconSize={6} wrapperStyle={{ fontSize: 11 }} />
                {categoryKeys.map(key => (
                  <Bar key={key} dataKey={key} fill={categoryColors[key] || '#6366f1'} radius={[2, 2, 0, 0]} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Weekly Comparison */}
        <div className="glass rounded-xl p-5">
          <div className="flex items-center justify-between mb-5">
            <h3 className="text-sm font-semibold text-text-primary">Weekly Comparison</h3>
            <div className="flex items-center gap-1 text-xs text-success">
              <TrendingUp size={12} /> {weeklyChange}% vs last week
            </div>
          </div>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.weekly_comparison}>
                <defs>
                  <linearGradient id="gradThis" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gradLast" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#64748b" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#64748b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="day" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Area type="monotone" dataKey="lastWeek" stroke="#64748b" strokeWidth={1.5} fill="url(#gradLast)" name="Last Week" strokeDasharray="4 4" />
                <Area type="monotone" dataKey="thisWeek" stroke="#6366f1" strokeWidth={2} fill="url(#gradThis)" name="This Week" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Department Performance */}
        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-semibold text-text-primary mb-5">Department Performance</h3>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="65%" data={data.department_performance}>
                <PolarGrid stroke="rgba(255,255,255,0.06)" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                <PolarRadiusAxis angle={30} domain={[0, 150]} stroke="rgba(255,255,255,0.04)" tick={{ fontSize: 9, fill: '#64748b' }} />
                <Radar name="Score" dataKey="score" stroke="#10b981" fill="#10b981" fillOpacity={0.15} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Prediction Accuracy */}
        <div className="glass rounded-xl p-5">
          <div className="flex items-center justify-between mb-5">
            <h3 className="text-sm font-semibold text-text-primary">Prediction vs Actual Risk</h3>
            <span className="px-2 py-0.5 rounded-md bg-success/10 text-success text-[10px] font-semibold">94.2% Accuracy</span>
          </div>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.prediction_timeline}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend iconType="circle" iconSize={6} wrapperStyle={{ fontSize: 11 }} />
                <Line type="monotone" dataKey="predicted" stroke="#6366f1" strokeWidth={2} dot={{ r: 3 }} name="Predicted" />
                <Line type="monotone" dataKey="actual" stroke="#f59e0b" strokeWidth={2} dot={{ r: 3 }} strokeDasharray="4 4" name="Actual" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Resource Utilization */}
        <div className="glass rounded-xl p-5 lg:col-span-2">
          <h3 className="text-sm font-semibold text-text-primary mb-5">Resource Utilization vs Target</h3>
          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.resource_utilization} barGap={4}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} domain={[0, 100]} />
                <Tooltip contentStyle={tooltipStyle} />
                <Legend iconType="circle" iconSize={6} wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="utilized" fill="#6366f1" radius={[3, 3, 0, 0]} name="Utilized %" barSize={20} />
                <Bar dataKey="target" fill="rgba(255,255,255,0.08)" radius={[3, 3, 0, 0]} name="Target %" barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
