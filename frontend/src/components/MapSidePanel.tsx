import React, { useState, useEffect } from 'react';
import { AlertCircle, Shield, Info, Truck, Radio, Navigation, Clock, User, Compass } from 'lucide-react';

interface ComplaintData {
  id: number;
  category: string;
  description: string;
  ward: string;
  severity: string;
  status: string;
  lat: number;
  lng: number;
  created_at?: string;
  assigned_department?: string;
}

interface ResourceData {
  id: number;
  type: string;
  name: string;
  status: string;
  ward: string;
  lat: number;
  lng: number;
}

interface WardData {
  name: string;
  coordinates: [number, number][];
  risk: string;
  score: number;
  details: {
    complaints: number;
    weather: string;
    resources: string;
    population: string;
  };
}

interface NearbyResource {
  id: number;
  type: string;
  name: string;
  status: string;
  ward: string;
  lat: number;
  lng: number;
  distance_km: number;
}

interface MapSidePanelProps {
  selectedComplaint: ComplaintData | null;
  selectedResource: ResourceData | null;
  selectedWard: WardData | null;
  onClearSelection: () => void;
}

const RISK_CONFIG: Record<string, { color: string; bg: string }> = {
  Green: { color: 'text-success', bg: 'bg-success/15' },
  Yellow: { color: 'text-warning', bg: 'bg-warning/15' },
  Orange: { color: 'text-orange-500', bg: 'bg-orange-500/15' },
  Red: { color: 'text-danger', bg: 'bg-danger/15' },
};

const SEVERITY_COLOR: Record<string, string> = {
  Critical: 'text-danger bg-danger/10 border-danger/20',
  High: 'text-orange-500 bg-orange-500/10 border-orange-500/20',
  Medium: 'text-warning bg-warning/10 border-warning/20',
  Low: 'text-success bg-success/10 border-success/20',
};

export const MapSidePanel: React.FC<MapSidePanelProps> = ({
  selectedComplaint,
  selectedResource,
  selectedWard,
  onClearSelection,
}) => {
  const [nearbyResources, setNearbyResources] = useState<NearbyResource[]>([]);
  const [searchRadius, setSearchRadius] = useState(5.0);
  const [loadingNearby, setLoadingNearby] = useState(false);

  // Fetch nearby resources when selectedComplaint or searchRadius changes
  useEffect(() => {
    if (!selectedComplaint) {
      setNearbyResources([]);
      return;
    }

    setLoadingNearby(true);
    fetch(`http://localhost:8000/map/nearby-resources?lat=${selectedComplaint.lat}&lng=${selectedComplaint.lng}&radius_km=${searchRadius}`)
      .then((res) => res.json())
      .then((json) => {
        if (json.success && json.data) {
          setNearbyResources(json.data);
        }
      })
      .catch((err) => console.error('Error loading nearby resources:', err))
      .finally(() => setLoadingNearby(false));
  }, [selectedComplaint, searchRadius]);

  const handleDeployResource = (resourceId: number) => {
    alert(`Deploying resource ID ${resourceId} to solve complaint: "${selectedComplaint?.category}"`);
  };

  return (
    <div className="w-80 glass rounded-xl border border-border flex flex-col h-full overflow-hidden shadow-2xl">
      {/* ── Panel Header ────────────────────────────────────────────── */}
      <div className="px-5 py-4 border-b border-border/40 flex items-center justify-between bg-white/[0.02]">
        <h2 className="text-sm font-bold text-text-primary uppercase tracking-wider flex items-center gap-2">
          <Radio size={14} className="text-primary animate-pulse" />
          Intelligence Desk
        </h2>
        {(selectedComplaint || selectedResource || selectedWard) && (
          <button
            onClick={onClearSelection}
            className="text-[10px] text-text-muted hover:text-text-primary px-2 py-0.5 rounded hover:bg-white/5 border border-border transition-all"
          >
            Clear Selection
          </button>
        )}
      </div>

      {/* ── Panel Content ──────────────────────────────────────────── */}
      <div className="flex-1 p-5 overflow-y-auto space-y-5">
        {selectedComplaint ? (
          // ── COMPLAINT CARD DETAIL ──
          <div className="space-y-4 fade-in">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider">Incident Details</span>
                <h3 className="text-sm font-bold text-text-primary mt-0.5 leading-tight">{selectedComplaint.category}</h3>
              </div>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${SEVERITY_COLOR[selectedComplaint.severity] || 'text-primary'}`}>
                {selectedComplaint.severity.toUpperCase()}
              </span>
            </div>

            <div className="bg-background/30 rounded-lg p-3 border border-border/30 text-xs text-text-secondary leading-relaxed">
              {selectedComplaint.description}
            </div>

            <div className="grid grid-cols-2 gap-2 text-[10px] border-b border-border/20 pb-4">
              <div className="bg-white/[0.02] p-2 rounded border border-border/30">
                <span className="text-text-muted block uppercase">Ward</span>
                <span className="text-text-primary font-bold text-xs">{selectedComplaint.ward}</span>
              </div>
              <div className="bg-white/[0.02] p-2 rounded border border-border/30">
                <span className="text-text-muted block uppercase">Status</span>
                <span className="text-text-primary font-bold text-xs">{selectedComplaint.status}</span>
              </div>
              {selectedComplaint.assigned_department && (
                <div className="col-span-2 bg-white/[0.02] p-2 rounded border border-border/30">
                  <span className="text-text-muted block uppercase">Assigned Team</span>
                  <span className="text-text-primary font-medium text-xs flex items-center gap-1">
                    <User size={12} className="text-primary-light" />
                    {selectedComplaint.assigned_department}
                  </span>
                </div>
              )}
            </div>

            {/* ── NEARBY RESOURCES SEARCH ── */}
            <div className="space-y-3 pt-2">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-text-primary flex items-center gap-1.5">
                  <Navigation size={12} className="text-primary" />
                  Nearby Dispatch
                </h4>
                <div className="flex items-center gap-1">
                  <span className="text-[10px] text-text-muted">Radius:</span>
                  <select
                    value={searchRadius}
                    onChange={(e) => setSearchRadius(parseFloat(e.target.value))}
                    className="bg-background/80 text-[10px] text-text-primary rounded border border-border/60 py-0.5 px-1 focus:outline-none focus:border-primary"
                  >
                    <option value={2.0}>2 km</option>
                    <option value={5.0}>5 km</option>
                    <option value={10.0}>10 km</option>
                  </select>
                </div>
              </div>

              {loadingNearby ? (
                <div className="space-y-2">
                  <div className="h-10 skeleton w-full"></div>
                  <div className="h-10 skeleton w-full"></div>
                </div>
              ) : nearbyResources.length === 0 ? (
                <div className="text-center py-4 bg-background/25 rounded border border-dashed border-border/50">
                  <AlertCircle size={16} className="text-text-muted mx-auto mb-1.5" />
                  <p className="text-[10px] text-text-muted">No resources available within {searchRadius}km</p>
                </div>
              ) : (
                <div className="space-y-2 max-h-56 overflow-y-auto">
                  {nearbyResources.map((res) => (
                    <div key={res.id} className="bg-white/[0.02] border border-border/40 p-2.5 rounded-lg flex items-center justify-between hover:bg-white/[0.04] transition-all">
                      <div>
                        <div className="font-semibold text-xs text-text-primary leading-tight">{res.name}</div>
                        <div className="text-[9px] text-text-secondary mt-0.5 flex items-center gap-1">
                          <Truck size={10} className="text-text-muted" />
                          {res.type} &bull; <span className="font-bold text-primary">{res.distance_km} km away</span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeployResource(res.id)}
                        disabled={res.status !== 'Available'}
                        className={`text-[9px] font-bold px-2 py-1 rounded transition-all active:scale-95 ${
                          res.status === 'Available'
                            ? 'bg-primary hover:bg-primary-light text-white shadow-md'
                            : 'bg-white/5 text-text-muted cursor-not-allowed border border-border/40'
                        }`}
                      >
                        {res.status === 'Available' ? 'Deploy' : res.status}
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : selectedResource ? (
          // ── RESOURCE CARD DETAIL ──
          <div className="space-y-4 fade-in">
            <div>
              <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider">Asset Properties</span>
              <h3 className="text-sm font-bold text-text-primary mt-0.5">{selectedResource.name}</h3>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="flex justify-between py-2 border-b border-border/20">
                <span className="text-text-muted">Asset Class</span>
                <span className="text-text-primary font-semibold flex items-center gap-1.5">
                  <Truck size={13} className="text-primary-light" />
                  {selectedResource.type}
                </span>
              </div>
              <div className="flex justify-between py-2 border-b border-border/20">
                <span className="text-text-muted">Operational State</span>
                <span className="text-text-primary font-semibold">{selectedResource.status}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-border/20">
                <span className="text-text-muted">Assigned Base Ward</span>
                <span className="text-text-primary font-semibold">{selectedResource.ward}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-border/20">
                <span className="text-text-muted">Coordinates</span>
                <span className="text-text-primary font-mono text-[10px]">
                  {selectedResource.lat.toFixed(4)}, {selectedResource.lng.toFixed(4)}
                </span>
              </div>
            </div>
          </div>
        ) : selectedWard ? (
          // ── WARD CARD DETAIL ──
          <div className="space-y-4 fade-in">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider">Regional Metrics</span>
                <h3 className="text-sm font-bold text-text-primary mt-0.5">{selectedWard.name}</h3>
              </div>
              <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${RISK_CONFIG[selectedWard.risk]?.bg} ${RISK_CONFIG[selectedWard.risk]?.color}`}>
                {selectedWard.risk.toUpperCase()}
              </span>
            </div>

            <div className="text-center py-4 bg-white/[0.01] border border-border/40 rounded-xl">
              <p className={`text-4xl font-black ${RISK_CONFIG[selectedWard.risk]?.color}`}>{selectedWard.score}</p>
              <p className="text-[9px] text-text-muted uppercase tracking-widest mt-1">Hazard Index Score</p>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-2 border-b border-border/20">
                <span className="text-text-muted">Active Complaints</span>
                <span className="text-text-primary font-bold">{selectedWard.details.complaints}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-border/20">
                <span className="text-text-muted">Weather Overlay</span>
                <span className="text-text-primary font-semibold">{selectedWard.details.weather}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-border/20">
                <span className="text-text-muted">Asset Allocation</span>
                <span className="text-text-primary font-semibold">{selectedWard.details.resources}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-border/20">
                <span className="text-text-muted">Est. Population</span>
                <span className="text-text-primary font-semibold">{selectedWard.details.population}</span>
              </div>
            </div>
          </div>
        ) : (
          // ── DEFAULT AI OP CENTER ──
          <div className="h-full flex flex-col justify-center py-6 text-center space-y-4 fade-in">
            <div className="w-12 h-12 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center mx-auto text-primary glow-primary">
              <Compass size={22} className="animate-spin-slow" />
            </div>
            <div>
              <h3 className="text-xs font-bold text-text-primary uppercase tracking-wider">Operational Overview</h3>
              <p className="text-[11px] text-text-secondary mt-1 max-w-[240px] mx-auto leading-relaxed">
                Click on any incident icon, dispatch vehicle, or ward region on the map to query properties, check nearby assets, or deploy emergency responses.
              </p>
            </div>

            <div className="pt-2 border-t border-border/40 text-left space-y-2.5">
              <h4 className="text-[10px] font-bold text-text-primary uppercase tracking-widest flex items-center gap-1.5">
                <Info size={11} className="text-primary-light" />
                GIS Dashboard Tips
              </h4>
              <ul className="text-[10px] text-text-muted space-y-1.5 list-disc pl-3">
                <li>Toggle <strong>AI Hotspots Forecast</strong> to view emergency predicted sectors.</li>
                <li>Write a natural query in the <strong>Search bar</strong> to filters items.</li>
                <li>Clustered markers split into separate items upon map zoom.</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
