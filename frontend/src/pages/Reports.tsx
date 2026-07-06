import { useState } from 'react';
import { FileText, Download, Loader2, Clock, CheckCircle } from 'lucide-react';

interface ReportType {
  title: string;
  description: string;
  lastGenerated: string;
  pages: number;
}

const reportTypes: ReportType[] = [
  {
    title: 'Morning Brief',
    description: 'Daily summary covering overnight incidents, weather forecast, AI-recommended focus areas, and resource deployment suggestions for the day ahead.',
    lastGenerated: '2 hours ago',
    pages: 8,
  },
  {
    title: 'Weekly Executive Report',
    description: 'Comprehensive performance breakdown including department KPIs, resource utilization trends, cost analysis, citizen satisfaction metrics, and prediction accuracy.',
    lastGenerated: '3 days ago',
    pages: 24,
  },
  {
    title: 'Emergency Risk Assessment',
    description: 'High-priority analysis of all current critical zones, weather-correlated risk predictions, required resource mobilization, and evacuation readiness status.',
    lastGenerated: '12 hours ago',
    pages: 12,
  },
];

const Reports = () => {
  const [loading, setLoading] = useState<string | null>(null);
  const [generated, setGenerated] = useState<string | null>(null);

  const generateReport = (type: string) => {
    setLoading(type);
    setGenerated(null);
    fetch('http://localhost:8000/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type }),
    })
      .then(res => res.json())
      .then(json => {
        setLoading(null);
        if (json.success && json.data && json.data.download_url) {
          setGenerated(type);
          window.open(json.data.download_url, '_blank');
          setTimeout(() => setGenerated(null), 3000);
        }
      })
      .catch(err => {
        console.error('Error generating report:', err);
        setLoading(null);
      });
  };

  return (
    <div className="space-y-6 fade-in">
      <div>
        <h1 className="text-2xl font-semibold text-text-primary tracking-tight flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-primary/20 flex items-center justify-center">
            <FileText size={20} className="text-primary" />
          </div>
          Automated Reports
        </h1>
        <p className="text-sm text-text-muted mt-2 ml-12">Generate AI-powered reports with actionable insights and recommendations</p>
      </div>

      <div className="space-y-3 max-w-4xl">
        {reportTypes.map((report) => (
          <div key={report.title} className="glass rounded-xl p-5 group hover:glass-hover transition-all duration-300">
            <div className="flex items-start justify-between gap-6">
              <div className="flex items-start gap-4 flex-1">
                <div className="w-10 h-10 rounded-lg bg-white/[0.03] border border-border flex items-center justify-center shrink-0 group-hover:border-primary/20 transition-colors">
                  <FileText size={18} className="text-text-muted group-hover:text-primary transition-colors" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-text-primary group-hover:text-primary-light transition-colors">{report.title}</h3>
                  <p className="text-xs text-text-muted mt-1.5 leading-relaxed max-w-xl">{report.description}</p>
                  <div className="flex items-center gap-4 mt-3 text-[10px] text-text-muted uppercase tracking-wider">
                    <span className="flex items-center gap-1"><Clock size={10} /> Last: {report.lastGenerated}</span>
                    <span>{report.pages} pages</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => generateReport(report.title)}
                disabled={loading === report.title}
                className={`px-5 py-2.5 rounded-lg text-xs font-medium flex items-center gap-2 transition-all min-w-[160px] justify-center shrink-0 ${
                  generated === report.title
                    ? 'bg-success/10 text-success border border-success/20'
                    : 'bg-white/[0.04] border border-border hover:border-primary/30 text-text-secondary hover:text-text-primary'
                }`}
              >
                {loading === report.title ? (
                  <><Loader2 className="animate-spin" size={14} /> Generating...</>
                ) : generated === report.title ? (
                  <><CheckCircle size={14} /> Ready</>
                ) : (
                  <><Download size={14} /> Generate PDF</>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Reports;
