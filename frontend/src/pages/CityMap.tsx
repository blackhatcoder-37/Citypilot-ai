import { useEffect, useState, useCallback } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Map as MapIcon, Clock, AlertTriangle } from 'lucide-react';

import { MapLayers } from '../components/MapLayers';
import { MapControls } from '../components/MapControls';
import { MapSidePanel } from '../components/MapSidePanel';

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

interface PredictionData {
  lat: number;
  lng: number;
  radius: number;
  risk_score: number;
  reason: string;
  ward: string;
}

const CityMap = () => {
  // Layer visibility toggles
  const [showMarkers, setShowMarkers] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [showWards, setShowWards] = useState(true);
  const [showPredictions, setShowPredictions] = useState(false);

  // Active dataset state
  const [complaints, setComplaints] = useState<ComplaintData[]>([]);
  const [resources, setResources] = useState<ResourceData[]>([]);
  const [heatmapPoints, setHeatmapPoints] = useState<[number, number, number][]>([]);
  const [wards, setWards] = useState<WardData[]>([]);
  const [predictions, setPredictions] = useState<PredictionData[]>([]);

  // Selected item states for the side panel
  const [selectedComplaint, setSelectedComplaint] = useState<ComplaintData | null>(null);
  const [selectedResource, setSelectedResource] = useState<ResourceData | null>(null);
  const [selectedWard, setSelectedWard] = useState<WardData | null>(null);

  // Filter indicator from AI search
  const [searchFilters, setSearchFilters] = useState<any>(null);

  // Load all map datasets dynamically
  const fetchAllMapData = useCallback(() => {
    // 1. Fetch complaints
    fetch('http://localhost:8000/map/complaints')
      .then((res) => res.json())
      .then((json) => {
        if (json.success && json.data) setComplaints(json.data);
      })
      .catch((err) => console.error('Complaints fetch error:', err));

    // 2. Fetch resources
    fetch('http://localhost:8000/map/resources')
      .then((res) => res.json())
      .then((json) => {
        if (json.success && json.data) setResources(json.data);
      })
      .catch((err) => console.error('Resources fetch error:', err));

    // 3. Fetch heatmap coordinates
    fetch('http://localhost:8000/map/heatmap')
      .then((res) => res.json())
      .then((json) => {
        if (json.success && json.data) setHeatmapPoints(json.data);
      })
      .catch((err) => console.error('Heatmap fetch error:', err));

    // 4. Fetch ward polygons
    fetch('http://localhost:8000/map/wards')
      .then((res) => res.json())
      .then((json) => {
        if (json.success && json.data && json.data.wards) {
          setWards(json.data.wards);
        }
      })
      .catch((err) => console.error('Wards fetch error:', err));

    // 5. Fetch predictions
    fetch('http://localhost:8000/map/predictions')
      .then((res) => res.json())
      .then((json) => {
        if (json.success && json.data) setPredictions(json.data);
      })
      .catch((err) => console.error('Predictions fetch error:', err));

    // Reset filter banner
    setSearchFilters(null);
  }, []);

  useEffect(() => {
    fetchAllMapData();
  }, [fetchAllMapData]);

  // AI search parser submission
  const handleAISearch = async (query: string) => {
    try {
      const res = await fetch('http://localhost:8000/map/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      const json = await res.json();
      if (json.success && json.data) {
        setComplaints(json.data.complaints);
        setResources(json.data.resources);
        setSearchFilters(json.data.filters);
        
        // Clear active panels selections since filtered items might have changed
        setSelectedComplaint(null);
        setSelectedResource(null);
        setSelectedWard(null);
      }
    } catch (err) {
      console.error('AI search submission error:', err);
    }
  };

  const handleResetData = () => {
    fetchAllMapData();
    setSelectedComplaint(null);
    setSelectedResource(null);
    setSelectedWard(null);
  };

  const handleSelectComplaint = (c: ComplaintData) => {
    setSelectedComplaint(c);
    setSelectedResource(null);
    setSelectedWard(null);
  };

  const handleSelectResource = (r: ResourceData) => {
    setSelectedResource(r);
    setSelectedComplaint(null);
    setSelectedWard(null);
  };

  const handleSelectWard = (w: WardData) => {
    setSelectedWard(w);
    setSelectedComplaint(null);
    setSelectedResource(null);
  };

  const handleClearSelection = () => {
    setSelectedComplaint(null);
    setSelectedResource(null);
    setSelectedWard(null);
  };

  // Convert active filters to a readable description list
  const renderActiveFilters = () => {
    if (!searchFilters) return null;
    const active = [];
    if (searchFilters.complaint_category) active.push(`Category: ${searchFilters.complaint_category}`);
    if (searchFilters.complaint_severity) active.push(`Severity: ${searchFilters.complaint_severity}`);
    if (searchFilters.complaint_status) active.push(`Status: ${searchFilters.complaint_status}`);
    if (searchFilters.resource_type) active.push(`Asset: ${searchFilters.resource_type}`);
    if (searchFilters.resource_status) active.push(`State: ${searchFilters.resource_status}`);
    if (searchFilters.ward) active.push(`Location: ${searchFilters.ward}`);
    if (searchFilters.text_search) active.push(`Search: "${searchFilters.text_search}"`);

    if (active.length === 0) return null;

    return (
      <div className="flex items-center gap-2 bg-primary/10 border border-primary/20 rounded-lg py-1.5 px-3 text-xs text-primary-light">
        <AlertTriangle size={12} className="animate-pulse" />
        <span className="font-semibold">AI Filter Active:</span>
        <span className="text-text-secondary">{active.join(' | ')}</span>
      </div>
    );
  };

  return (
    <div className="flex-1 flex flex-col min-h-0 space-y-4 fade-in">
      {/* Header Row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-primary/20 flex items-center justify-center">
            <MapIcon size={20} className="text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-text-primary tracking-tight">Smart City GIS Operations</h1>
            <p className="text-xs text-text-muted mt-0.5">Dynamic PostgreSQL GIS Mapping & AI Forecaster</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {renderActiveFilters()}
          <div className="flex items-center gap-2 text-xs text-text-muted bg-card px-3 py-1.5 rounded-lg border border-border">
            <Clock size={12} />
            <span>Updates: Live (PostgreSQL)</span>
          </div>
        </div>
      </div>

      {/* Main Map + Panel Row */}
      <div className="flex gap-4 flex-1 min-h-0">
        {/* Map Container Wrapper */}
        <div className="flex-1 glass rounded-xl overflow-hidden relative border border-border">
          <MapContainer
            center={[28.6139, 77.209]} // Centered on Delhi base
            zoom={12}
            style={{ height: '100%', width: '100%', zIndex: 1 }}
          >
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
              maxZoom={18}
            />
            
            <MapLayers
              showMarkers={showMarkers}
              showHeatmap={showHeatmap}
              showWards={showWards}
              showPredictions={showPredictions}
              complaints={complaints}
              resources={resources}
              heatmapPoints={heatmapPoints}
              wards={wards}
              predictions={predictions}
              onSelectComplaint={handleSelectComplaint}
              onSelectResource={handleSelectResource}
              onSelectWard={handleSelectWard}
            />
          </MapContainer>

          {/* Floating Controls Overlay */}
          <MapControls
            showMarkers={showMarkers}
            setShowMarkers={setShowMarkers}
            showHeatmap={showHeatmap}
            setShowHeatmap={setShowHeatmap}
            showWards={showWards}
            setShowWards={setShowWards}
            showPredictions={showPredictions}
            setShowPredictions={setShowPredictions}
            onSearch={handleAISearch}
            onReset={handleResetData}
          />
        </div>

        {/* Side Panel Wrapper */}
        <MapSidePanel
          selectedComplaint={selectedComplaint}
          selectedResource={selectedResource}
          selectedWard={selectedWard}
          onClearSelection={handleClearSelection}
        />
      </div>
    </div>
  );
};

export default CityMap;
