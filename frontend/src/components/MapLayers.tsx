import React, { useEffect } from 'react';
import { useMap, Polygon, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';
import 'leaflet.markercluster';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';

// SVG paths for Lucide-like icons inside custom DivIcons
const SVG_ICONS: Record<string, string> = {
  // Complaint Categories
  Flood: `<path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10zM12 6v6h6" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/><path d="M8 14c1.5-1.5 3-1.5 4.5 0 1.5 1.5 3 1.5 4.5 0" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>`,
  Garbage: `<path d="M3 6h18M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2M10 11v6M14 11v6" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`,
  Traffic: `<rect x="5" y="2" width="14" height="20" rx="2" stroke="currentColor" stroke-width="2" fill="none"/><circle cx="12" cy="7" r="2.5" fill="currentColor"/><circle cx="12" cy="12" r="2.5" fill="currentColor"/><circle cx="12" cy="17" r="2.5" fill="currentColor"/>`,
  'Water Leakage': `<path d="M12 22a7 7 0 0 0 7-7c0-4.3-7-13-7-13S5 10.7 5 15a7 7 0 0 0 7 7z" stroke="currentColor" stroke-width="2" fill="none" stroke-linejoin="round"/>`,
  'Power Outage': `<path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`,
  'Street Light': `<path d="M12 2v2M5 12h14M12 12v8M9 20h6M7.5 7.5l1.5 1.5M16.5 7.5l-1.5 1.5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>`,
  'Road Damage': `<path d="M4 22h16M10 14l-4 8M14 14l4 8M6 14h12M12 2v6M9 6l3-3 3 3" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`,
  'Medical Emergency': `<path d="M22 12h-4l-3 9L9 3l-3 9H2" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`,
  Sewage: `<path d="M12 2L2 22h20L12 2z" stroke="currentColor" stroke-width="2" fill="none" stroke-linejoin="round"/><path d="M12 9v4M12 17h.01" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/>`,

  // Resource Types
  'Garbage Truck': `<path d="M14 18H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h8M14 6h3l4 4v6a2 2 0 0 1-2 2h-5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/><circle cx="7.5" cy="18.5" r="2.5" fill="currentColor"/><circle cx="16.5" cy="18.5" r="2.5" fill="currentColor"/>`,
  'Fire Truck': `<path d="M7.5 18.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM16.5 18.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z" fill="currentColor"/><path d="M14 18H6a2 2 0 0 1-2-2V8h10v10zM14 10h4l3 3v3h-7v-6zM11 6h2M8 4h2" stroke="currentColor" stroke-width="2" fill="none"/>`,
  Ambulance: `<rect x="2" y="6" width="16" height="12" rx="2" stroke="currentColor" stroke-width="2" fill="none"/><path d="M18 10h3l3 3v5h-6v-8z" stroke="currentColor" stroke-width="2" fill="none"/><circle cx="6" cy="18" r="2" fill="currentColor"/><circle cx="14" cy="18" r="2" fill="currentColor"/><path d="M10 9v6M7 12h6" stroke="currentColor" stroke-width="2"/>`,
  'Water Pump': `<path d="M21 10h-6V4H9v6H3v4h6v6h6v-6h6z" stroke="currentColor" stroke-width="2" fill="none" stroke-linejoin="round"/>`,
  'Police Vehicle': `<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="currentColor" stroke-width="2" fill="none" stroke-linejoin="round"/>`,
  Staff: `<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"/><circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2" fill="none"/>`,
  
  // Unknown Fallback
  default: `<circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/><path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="2"/>`,
};

// Color configuration maps
const SEVERITY_COLORS: Record<string, string> = {
  Critical: '#ef4444', // red
  High: '#f97316',     // orange
  Medium: '#eab308',   // yellow
  Low: '#10b981',      // green
};

const RESOURCE_STATUS_COLORS: Record<string, string> = {
  Available: '#10b981',       // green
  Deployed: '#3b82f6',        // blue
  Maintenance: '#eab308',     // yellow
  'Out of Service': '#ef4444', // red
};

const RISK_COLORS: Record<string, string> = {
  Green: '#10b981',
  Yellow: '#eab308',
  Orange: '#f97316',
  Red: '#ef4444',
};

// Component props
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

interface MapLayersProps {
  showMarkers: boolean;
  showHeatmap: boolean;
  showWards: boolean;
  showPredictions: boolean;
  complaints: ComplaintData[];
  resources: ResourceData[];
  heatmapPoints: [number, number, number][];
  wards: WardData[];
  predictions: PredictionData[];
  onSelectComplaint: (complaint: ComplaintData) => void;
  onSelectResource: (resource: ResourceData) => void;
  onSelectWard: (ward: WardData) => void;
}

export const MapLayers: React.FC<MapLayersProps> = ({
  showMarkers,
  showHeatmap,
  showWards,
  showPredictions,
  complaints,
  resources,
  heatmapPoints,
  wards,
  predictions,
  onSelectComplaint,
  onSelectResource,
  onSelectWard,
}) => {
  const map = useMap();

  // ── Render Heatmap Layer ──────────────────────────────────────────
  useEffect(() => {
    if (!map) return;
    if (!showHeatmap || heatmapPoints.length === 0) return;

    const heatLayer = (L as any).heatLayer(heatmapPoints, {
      radius: 28,
      blur: 18,
      maxZoom: 15,
      max: 1.0,
      gradient: {
        0.2: 'rgba(59, 130, 246, 0.5)',   // Blue
        0.4: 'rgba(16, 185, 129, 0.7)',   // Green
        0.6: 'rgba(234, 179, 8, 0.85)',   // Yellow
        0.8: 'rgba(249, 115, 22, 0.95)',  // Orange
        1.0: 'rgba(239, 68, 68, 1.0)'     // Red
      }
    });

    heatLayer.addTo(map);

    return () => {
      map.removeLayer(heatLayer);
    };
  }, [map, showHeatmap, heatmapPoints]);

  // ── Render Clustered Markers (Complaints & Resources) ─────────────
  useEffect(() => {
    if (!map) return;
    if (!showMarkers) return;

    // Initialize marker cluster group
    const clusterGroup = (L as any).markerClusterGroup({
      showCoverageOnHover: false,
      zoomToBoundsOnClick: true,
      maxClusterRadius: 40,
      spiderfyOnMaxZoom: true,
    });

    // 1. Add Complaints Markers
    complaints.forEach((c) => {
      if (c.lat === undefined || c.lng === undefined) return;
      const color = SEVERITY_COLORS[c.severity] || '#6366f1';
      const iconMarkup = SVG_ICONS[c.category] || SVG_ICONS.default;

      const divIcon = L.divIcon({
        className: 'custom-gps-marker',
        html: `
          <div class="relative flex items-center justify-center w-8 h-8 rounded-full shadow-lg border border-white/20 transition-all duration-300 hover:scale-110 cursor-pointer" style="background-color: ${color}">
            <div class="absolute -inset-1.5 rounded-full opacity-20 animate-ping" style="background-color: ${color}"></div>
            <svg class="w-4.5 h-4.5 text-white" viewBox="0 0 24 24" fill="none">
              ${iconMarkup}
            </svg>
          </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, -16],
      });

      const popupContent = `
        <div class="text-xs space-y-1.5">
          <div class="flex items-center justify-between gap-4">
            <span class="font-bold text-sm tracking-tight text-white">${c.category}</span>
            <span class="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase" style="background-color: ${color}20; color: ${color}">
              ${c.severity}
            </span>
          </div>
          <p class="text-gray-300 line-clamp-2">${c.description}</p>
          <div class="text-[10px] text-gray-400 font-medium">Ward: ${c.ward} | Status: <span class="text-white font-semibold">${c.status}</span></div>
          <button class="w-full mt-2 py-1 px-2 rounded bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-[10px] tracking-wide transition-all" onclick="window.dispatchComplaintClick(${c.id})">
            Analyze Nearby Resources
          </button>
        </div>
      `;

      const marker = L.marker([c.lat, c.lng], { icon: divIcon });
      marker.bindPopup(popupContent, {
        closeButton: false,
        className: 'custom-leaflet-popup',
        maxWidth: 240,
      });

      marker.on('click', () => {
        onSelectComplaint(c);
      });

      clusterGroup.addLayer(marker);
    });

    // 2. Add Resources Markers
    resources.forEach((r) => {
      if (r.lat === undefined || r.lng === undefined) return;
      const color = RESOURCE_STATUS_COLORS[r.status] || '#94a3b8';
      const iconMarkup = SVG_ICONS[r.type] || SVG_ICONS.default;

      const divIcon = L.divIcon({
        className: 'custom-gps-marker',
        html: `
          <div class="relative flex items-center justify-center w-8 h-8 rounded-lg shadow-lg border border-white/20 transition-all duration-300 hover:scale-110 cursor-pointer" style="background-color: ${color}">
            <svg class="w-4.5 h-4.5 text-white" viewBox="0 0 24 24" fill="none">
              ${iconMarkup}
            </svg>
          </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, -16],
      });

      const popupContent = `
        <div class="text-xs space-y-1">
          <div class="flex items-center justify-between gap-4">
            <span class="font-bold text-sm tracking-tight text-white">${r.name}</span>
            <span class="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase" style="background-color: ${color}20; color: ${color}">
              ${r.status}
            </span>
          </div>
          <p class="text-gray-300">Type: <strong>${r.type}</strong></p>
          <p class="text-[10px] text-gray-400">Deployed in ${r.ward}</p>
        </div>
      `;

      const marker = L.marker([r.lat, r.lng], { icon: divIcon });
      marker.bindPopup(popupContent, {
        closeButton: false,
        className: 'custom-leaflet-popup',
        maxWidth: 240,
      });

      marker.on('click', () => {
        onSelectResource(r);
      });

      clusterGroup.addLayer(marker);
    });

    map.addLayer(clusterGroup);

    // Expose callback globally so Leaflet popup buttons can trigger it
    (window as any).dispatchComplaintClick = (id: number) => {
      const selected = complaints.find((comp) => comp.id === id);
      if (selected) {
        onSelectComplaint(selected);
        const popups = document.querySelectorAll('.leaflet-popup');
        popups.forEach((p) => p.remove()); // Programmatically close popups
      }
    };

    return () => {
      map.removeLayer(clusterGroup);
      delete (window as any).dispatchComplaintClick;
    };
  }, [map, showMarkers, complaints, resources, onSelectComplaint, onSelectResource]);

  return (
    <>
      {/* ── Render Ward Polygons ────────────────────────────────────── */}
      {showWards &&
        wards.map((w, index) => {
          const color = RISK_COLORS[w.risk] || '#10b981';
          return (
            <Polygon
              key={`ward-${index}`}
              positions={w.coordinates}
              pathOptions={{
                fillColor: color,
                color: color,
                fillOpacity: 0.12,
                weight: 1.5,
                dashArray: '3, 4',
              }}
              eventHandlers={{
                mouseover: (e) => {
                  const layer = e.target;
                  layer.setStyle({
                    fillOpacity: 0.28,
                    weight: 2.5,
                  });
                },
                mouseout: (e) => {
                  const layer = e.target;
                  layer.setStyle({
                    fillOpacity: 0.12,
                    weight: 1.5,
                  });
                },
                click: () => {
                  onSelectWard(w);
                },
              }}
            >
              <Popup className="custom-leaflet-popup">
                <div className="text-xs space-y-1">
                  <h4 className="font-bold text-sm text-white">{w.name}</h4>
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }}></span>
                    <span className="text-gray-300">
                      Risk Index: <strong style={{ color }}>{w.risk} ({w.score}/100)</strong>
                    </span>
                  </div>
                  <div className="border-t border-white/5 mt-1.5 pt-1.5 space-y-0.5 text-gray-400 text-[10px]">
                    <div>Active Complaints: <span className="text-white font-semibold">{w.details.complaints}</span></div>
                    <div>Resource Coverage: <span className="text-white font-semibold">{w.details.resources}</span></div>
                  </div>
                </div>
              </Popup>
            </Polygon>
          );
        })}

      {/* ── Render Predicted Hotspots ───────────────────────────────── */}
      {showPredictions &&
        predictions.map((p, index) => {
          const color = '#ec4899'; // Vibrant pink for predicted emergency areas
          return (
            <Circle
              key={`pred-${index}`}
              center={[p.lat, p.lng]}
              radius={p.radius}
              pathOptions={{
                fillColor: color,
                color: color,
                fillOpacity: 0.08,
                weight: 2,
                dashArray: '5, 8',
                className: 'animate-pulse-glow',
              }}
            >
              <Popup className="custom-leaflet-popup">
                <div className="text-xs space-y-1.5 max-w-xs">
                  <div className="flex items-center justify-between gap-4 border-b border-pink-500/20 pb-1">
                    <span className="font-bold text-sm tracking-tight text-white flex items-center gap-1">
                      <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-pink-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-pink-500"></span>
                      </span>
                      AI Hotspot Forecast
                    </span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-pink-500/20 text-pink-400">
                      RISK: {p.risk_score}%
                    </span>
                  </div>
                  <div className="text-pink-100 font-medium">Cluster Location: {p.ward}</div>
                  <p className="text-gray-300 leading-relaxed text-[11px]">{p.reason}</p>
                  <p className="text-[9px] text-gray-500 italic mt-1">Forecast range radius: {p.radius}m</p>
                </div>
              </Popup>
            </Circle>
          );
        })}
    </>
  );
};
