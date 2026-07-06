import { useState } from 'react';
import {
  Search, BrainCircuit, AlertTriangle, ShieldCheck,
  TrendingDown, Target, Zap, FileText, Loader2,
  CheckCircle, BarChart3, MapPin, Lightbulb, Clock, BookOpen, AlertOctagon, RotateCcw
} from 'lucide-react';

interface AnalysisResult {
  executive_summary: string;
  risk_score: number;
  confidence: number | string;
  priority_level: string;
  recommendations: string[];
  predicted_hotspots: any[];
  affected_wards: string[];
  required_resources: string[];
  estimated_resolution_time: string;
  sources: string[];

  // Fallback legacy support if returned by older models
  evidence?: string[];
  recommendation?: string;
  affected_areas?: string[];
  priority?: string;
  resources_needed?: string[];
}

const suggestedQueries = [
  'What should I focus on today?',
  'Which area is at highest risk right now?',
  'What happens if rainfall increases by 30%?',
  'What resources should I deploy to Ward 2?',
  'Show me the flood risk assessment',
];

const AICommandCenter = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const runAnalysis = (q?: string) => {
    const searchQuery = q || query;
    if (!searchQuery.trim()) return;
    
    setQuery(searchQuery);
    setLoading(true);
    setError(null);
    setResult(null);

    fetch('http://localhost:8000/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: searchQuery }),
    })
      .then(res => {
        if (!res.ok) {
          throw new Error(`Server error: status ${res.status}`);
        }
        return res.json();
      })
      .then(json => {
        if (json.success && json.data) {
          setResult(json.data);
        } else {
          setError(json.message || 'Analysis failed. Please try again.');
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Analysis error:', err);
        setError('Could not connect to the CityPilot AI backend. Please verify the server is running on port 8000 and try again.');
        setLoading(false);
      });
  };

  const downloadReport = () => {
    fetch('http://localhost:8000/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: 'Emergency Risk Assessment' }),
    })
      .then(res => res.json())
      .then(json => {
        if (json.success && json.data && json.data.download_url) {
          window.open(json.data.download_url, '_blank');
        }
      })
      .catch(err => console.error('Error generating PDF report:', err));
  };

  const getPriorityColor = (level: string) => {
    const l = level ? level.toUpperCase() : 'MEDIUM';
    if (l === 'CRITICAL') return 'bg-danger/20 text-danger border-danger/30';
    if (l === 'HIGH') return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
    if (l === 'LOW') return 'bg-success/20 text-success border-success/30';
    return 'bg-warning/20 text-warning border-warning/30';
  };

  const getRiskColor = (score: number) => {
    if (score >= 70) return 'text-danger';
    if (score >= 40) return 'text-warning';
    return 'text-success';
  };

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-text-primary tracking-tight flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-primary/20 flex items-center justify-center">
            <BrainCircuit size={20} className="text-primary" />
          </div>
          AI Command Center
        </h1>
        <p className="text-sm text-text-muted mt-2 ml-12">Ask complex questions about city operations. Get actionable intelligence.</p>
      </div>

      {/* Search Bar */}
      <div className="glass rounded-xl p-6 glow-primary">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-text-muted" size={20} />
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && runAnalysis()}
            className="w-full bg-white/[0.03] border border-border text-text-primary rounded-xl pl-12 pr-4 py-4 text-sm focus:outline-none focus:border-primary/40 transition-all placeholder-text-muted"
            placeholder="Ask the AI: 'What should I focus on today?' or 'Which area is at highest risk?'"
          />
        </div>

        {/* Suggested Queries */}
        <div className="flex flex-wrap gap-2 mt-4">
          {suggestedQueries.map((sq) => (
            <button
              key={sq}
              onClick={() => runAnalysis(sq)}
              className="px-3 py-1.5 rounded-lg bg-white/[0.03] border border-border text-xs text-text-secondary hover:text-text-primary hover:border-border-hover transition-all"
            >
              {sq}
            </button>
          ))}
        </div>

        <button
          onClick={() => runAnalysis()}
          disabled={loading || !query.trim()}
          className="mt-4 w-full bg-primary hover:bg-primary-light text-white font-medium text-sm py-3.5 rounded-xl transition-all flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {loading ? (
            <><Loader2 className="animate-spin" size={18} /> Analyzing city data...</>
          ) : (
            <><Zap size={16} /> Run City Analysis</>
          )}
        </button>
      </div>

      {/* Error State */}
      {error && (
        <div className="glass border-danger/30 rounded-xl p-6 flex flex-col md:flex-row items-center gap-4 animate-shake">
          <div className="w-12 h-12 rounded-full bg-danger/10 flex items-center justify-center text-danger shrink-0">
            <AlertOctagon size={24} />
          </div>
          <div className="flex-1 text-center md:text-left space-y-1">
            <h4 className="text-sm font-semibold text-text-primary">Operational Connection Error</h4>
            <p className="text-xs text-text-muted">{error}</p>
          </div>
          <button
            onClick={() => runAnalysis()}
            className="px-4 py-2 bg-white/[0.04] border border-border hover:bg-white/[0.08] rounded-lg text-xs text-text-primary font-semibold flex items-center gap-2 transition-all shrink-0"
          >
            <RotateCcw size={14} /> Retry Analysis
          </button>
        </div>
      )}

      {/* Results Section */}
      {result && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 fade-in">
          {/* Main Analysis Column */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Executive Summary */}
            <div className="glass rounded-xl p-6 border-l-4 border-l-primary relative overflow-hidden">
              <div className="absolute right-0 top-0 w-24 h-24 bg-primary/5 rounded-full blur-2xl" />
              <div className="flex items-center gap-2.5 mb-4">
                <Lightbulb size={18} className="text-warning animate-pulse" />
                <h3 className="text-sm font-bold text-text-primary uppercase tracking-wide">Executive Summary</h3>
              </div>
              <p className="text-sm text-text-secondary leading-relaxed font-normal whitespace-pre-wrap">
                {result.executive_summary}
              </p>
              <div className="mt-5 pt-4 border-t border-border flex items-center justify-between">
                <span className="text-[10px] text-text-muted font-mono">ENGINE: PostgreSQL + Gemini AI</span>
                <button 
                  onClick={downloadReport}
                  className="flex items-center gap-2 text-xs text-primary-light hover:text-primary font-medium transition-colors"
                >
                  <FileText size={14} /> Generate Formal PDF Report
                </button>
              </div>
            </div>

            {/* Recommendations */}
            <div className="glass rounded-xl p-6">
              <div className="flex items-center gap-2.5 mb-5">
                <Target size={18} className="text-primary" />
                <h3 className="text-sm font-bold text-text-primary uppercase tracking-wide">Tactical Recommendations</h3>
              </div>
              <div className="space-y-4">
                {(result.recommendations && result.recommendations.length > 0 ? result.recommendations : (result.evidence || [])).map((rec, i) => (
                  <div key={i} className="flex items-start gap-4 p-3.5 bg-white/[0.01] border border-border rounded-xl hover:bg-white/[0.02] transition-colors">
                    <div className="w-6 h-6 rounded-lg bg-primary/10 flex items-center justify-center text-primary font-bold text-xs shrink-0 mt-0.5">
                      {i + 1}
                    </div>
                    <p className="text-sm text-text-secondary leading-relaxed">{rec}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Predicted Hotspots */}
            <div className="glass rounded-xl p-6">
              <div className="flex items-center gap-2.5 mb-5">
                <AlertTriangle size={18} className="text-orange-400" />
                <h3 className="text-sm font-bold text-text-primary uppercase tracking-wide">AI Predicted Hazard Hotspots</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {result.predicted_hotspots && result.predicted_hotspots.length > 0 ? (
                  result.predicted_hotspots.map((hotspot, i) => {
                    const isStr = typeof hotspot === 'string';
                    const title = isStr ? hotspot : hotspot.ward;
                    const reason = isStr ? 'Spatial aggregation pattern detected.' : hotspot.reason;
                    const score = isStr ? result.risk_score : hotspot.risk_score;
                    return (
                      <div key={i} className="bg-white/[0.01] border border-border rounded-xl p-4 space-y-2 hover:border-border-hover transition-colors">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-xs text-text-primary">{title}</span>
                          <span className="px-2 py-0.5 rounded-md text-[9px] font-bold bg-danger/10 text-danger border border-danger/20">
                            {score}% RISK
                          </span>
                        </div>
                        <p className="text-xs text-text-muted leading-relaxed line-clamp-2">{reason}</p>
                      </div>
                    );
                  })
                ) : (
                  <div className="col-span-2 text-center py-6 text-xs text-text-muted italic bg-white/[0.01] border border-dashed border-border rounded-xl">
                    No immediate spatial hotspots forecasted.
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Metrics Column */}
          <div className="space-y-6">
            
            {/* KPI Dials */}
            <div className="grid grid-cols-2 gap-4">
              <div className="glass rounded-xl p-5 text-center relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1.5 bg-danger/40" />
                <p className="text-[10px] text-text-muted uppercase tracking-wider mb-2">Risk Index</p>
                <p className={`text-4xl font-extrabold tracking-tight ${getRiskColor(result.risk_score)}`}>
                  {result.risk_score}
                </p>
                <p className="text-[9px] text-text-muted mt-2">Scale score / 100</p>
              </div>

              <div className="glass rounded-xl p-5 text-center relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1.5 bg-success/40" />
                <p className="text-[10px] text-text-muted uppercase tracking-wider mb-2">Confidence</p>
                <p className="text-4xl font-extrabold text-success tracking-tight">
                  {typeof result.confidence === 'number' ? `${result.confidence}%` : result.confidence}
                </p>
                <p className="text-[9px] text-text-muted mt-2">Prediction accuracy</p>
              </div>
            </div>

            {/* Priority & Timing */}
            <div className="glass rounded-xl p-5 space-y-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <ShieldCheck size={14} className="text-primary-light" />
                  <span className="text-[11px] font-bold text-text-primary uppercase tracking-wide">Incident Priority</span>
                </div>
                <div className={`inline-block px-3 py-1.5 rounded-lg border text-xs font-bold tracking-widest ${getPriorityColor(result.priority_level || result.priority || 'MEDIUM')}`}>
                  {(result.priority_level || result.priority || 'MEDIUM').toUpperCase()}
                </div>
              </div>

              <div className="pt-3 border-t border-border flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <Clock size={13} className="text-text-muted" />
                    <span className="text-[10px] text-text-muted uppercase tracking-wide">Est. Resolution Time</span>
                  </div>
                  <p className="text-sm font-semibold text-text-primary">
                    {result.estimated_resolution_time || '12 - 24 hours'}
                  </p>
                </div>
              </div>
            </div>

            {/* Affected Wards */}
            <div className="glass rounded-xl p-5">
              <div className="flex items-center gap-2.5 mb-4">
                <MapPin size={15} className="text-info" />
                <h4 className="text-xs font-bold text-text-primary uppercase tracking-wide">Affected Wards</h4>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {(result.affected_wards && result.affected_wards.length > 0 ? result.affected_wards : (result.affected_areas || [])).map(ward => (
                  <span key={ward} className="px-2.5 py-1 bg-white/[0.04] border border-border rounded-md text-xs text-text-secondary">
                    {ward}
                  </span>
                ))}
              </div>
            </div>

            {/* Required Resources */}
            <div className="glass rounded-xl p-5">
              <div className="flex items-center gap-2.5 mb-4">
                <BarChart3 size={15} className="text-primary" />
                <h4 className="text-xs font-bold text-text-primary uppercase tracking-wide">Required Resources</h4>
              </div>
              <ul className="space-y-2.5">
                {(result.required_resources && result.required_resources.length > 0 ? result.required_resources : (result.resources_needed || [])).map((res, i) => (
                  <li key={i} className="flex items-center gap-2.5 text-xs text-text-secondary">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
                    <span className="truncate">{res}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Knowledge Sources */}
            <div className="glass rounded-xl p-5">
              <div className="flex items-center gap-2.5 mb-4">
                <BookOpen size={15} className="text-warning" />
                <h4 className="text-xs font-bold text-text-primary uppercase tracking-wide">Knowledge Sources Used</h4>
              </div>
              {result.sources && result.sources.length > 0 ? (
                <div className="space-y-2">
                  {result.sources.map((source, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs text-text-muted bg-white/[0.01] border border-border p-2 rounded-lg truncate">
                      <FileText size={12} className="text-primary-light shrink-0" />
                      <span className="truncate" title={source}>{source}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-text-muted italic">No external document files cited in this context.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AICommandCenter;
