import React, { useState } from 'react';
import { Layers, Search, RotateCcw, Compass, ShieldAlert, Thermometer, MapPin } from 'lucide-react';

interface MapControlsProps {
  showMarkers: boolean;
  setShowMarkers: (val: boolean) => void;
  showHeatmap: boolean;
  setShowHeatmap: (val: boolean) => void;
  showWards: boolean;
  setShowWards: (val: boolean) => void;
  showPredictions: boolean;
  setShowPredictions: (val: boolean) => void;
  onSearch: (query: string) => Promise<void>;
  onReset: () => void;
}

export const MapControls: React.FC<MapControlsProps> = ({
  showMarkers,
  setShowMarkers,
  showHeatmap,
  setShowHeatmap,
  showWards,
  setShowWards,
  showPredictions,
  setShowPredictions,
  onSearch,
  onReset,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);

  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      await onSearch(searchQuery);
    } catch (err) {
      console.error(err);
    } finally {
      setSearching(false);
    }
  };

  const handleClear = () => {
    setSearchQuery('');
    onReset();
  };

  return (
    <div className="absolute top-4 left-4 z-[1000] w-80 space-y-3">
      {/* ── Search Bar Panel ────────────────────────────────────────── */}
      <form onSubmit={handleSearchSubmit} className="glass rounded-xl shadow-xl p-2.5 flex items-center gap-2 border border-border">
        <div className="relative flex-1">
          <input
            type="text"
            placeholder="Ask AI (e.g. 'high traffic in ward 4')..."
            className="w-full bg-background/40 hover:bg-background/60 focus:bg-background/80 text-text-primary text-xs py-2 pl-8 pr-2.5 rounded-lg border border-border/60 focus:border-primary/80 focus:outline-none transition-all placeholder:text-text-muted"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <Search size={14} className="absolute left-2.5 top-2.5 text-text-muted" />
        </div>
        <button
          type="submit"
          disabled={searching}
          className="bg-primary hover:bg-primary-light text-white text-[10px] font-bold px-3 py-2 rounded-lg transition-all shadow-md active:scale-95 disabled:opacity-50"
        >
          {searching ? 'Parsing...' : 'Search'}
        </button>
        {searchQuery && (
          <button
            type="button"
            onClick={handleClear}
            className="p-2 rounded-lg text-text-muted hover:text-text-primary hover:bg-white/5 transition-all"
            title="Reset Filters"
          >
            <RotateCcw size={14} />
          </button>
        )}
      </form>

      {/* ── Layer Toggles Panel ──────────────────────────────────────── */}
      <div className="glass rounded-xl shadow-xl p-4 border border-border">
        <div className="flex items-center gap-2 border-b border-border/40 pb-2 mb-3">
          <Layers size={14} className="text-primary" />
          <h3 className="text-xs font-bold text-text-primary tracking-wide uppercase">Map Overlays</h3>
        </div>

        <div className="space-y-2.5">
          {/* Active Incidents / Markers */}
          <label className="flex items-center justify-between cursor-pointer group">
            <span className="flex items-center gap-2 text-xs text-text-secondary group-hover:text-text-primary transition-colors">
              <MapPin size={14} className={showMarkers ? 'text-primary' : 'text-text-muted'} />
              Incidents & Resources
            </span>
            <input
              type="checkbox"
              checked={showMarkers}
              onChange={(e) => setShowMarkers(e.target.checked)}
              className="sr-only peer"
            />
            <div className="relative w-8 h-4 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-text-secondary after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-primary peer-checked:after:bg-white border border-border/40"></div>
          </label>

          {/* Incident Density / Heatmap */}
          <label className="flex items-center justify-between cursor-pointer group">
            <span className="flex items-center gap-2 text-xs text-text-secondary group-hover:text-text-primary transition-colors">
              <Thermometer size={14} className={showHeatmap ? 'text-warning' : 'text-text-muted'} />
              Risk Density Heatmap
            </span>
            <input
              type="checkbox"
              checked={showHeatmap}
              onChange={(e) => setShowHeatmap(e.target.checked)}
              className="sr-only peer"
            />
            <div className="relative w-8 h-4 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-text-secondary after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-warning peer-checked:after:bg-white border border-border/40"></div>
          </label>

          {/* Ward Boundaries */}
          <label className="flex items-center justify-between cursor-pointer group">
            <span className="flex items-center gap-2 text-xs text-text-secondary group-hover:text-text-primary transition-colors">
              <Compass size={14} className={showWards ? 'text-success' : 'text-text-muted'} />
              Ward Boundaries
            </span>
            <input
              type="checkbox"
              checked={showWards}
              onChange={(e) => setShowWards(e.target.checked)}
              className="sr-only peer"
            />
            <div className="relative w-8 h-4 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-text-secondary after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-success peer-checked:after:bg-white border border-border/40"></div>
          </label>

          {/* Predictive Hotspots */}
          <label className="flex items-center justify-between cursor-pointer group">
            <span className="flex items-center gap-2 text-xs text-text-secondary group-hover:text-text-primary transition-colors">
              <ShieldAlert size={14} className={showPredictions ? 'text-pink-500' : 'text-text-muted'} />
              AI Hotspots Forecast
            </span>
            <input
              type="checkbox"
              checked={showPredictions}
              onChange={(e) => setShowPredictions(e.target.checked)}
              className="sr-only peer"
            />
            <div className="relative w-8 h-4 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-text-secondary after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-pink-500 peer-checked:after:bg-white border border-border/40"></div>
          </label>
        </div>
      </div>
    </div>
  );
};
