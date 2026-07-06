import * as L from 'leaflet';

declare module 'leaflet' {
  interface HeatLayerOptions {
    minOpacity?: number;
    maxZoom?: number;
    max?: number;
    radius?: number;
    blur?: number;
    gradient?: { [key: number]: string };
  }

  function heatLayer(
    latlngs: (L.LatLng | [number, number] | [number, number, number])[],
    options?: HeatLayerOptions
  ): L.Layer;
}
