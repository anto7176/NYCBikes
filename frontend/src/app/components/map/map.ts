import {
  AfterViewInit,
  Component,
  effect,
  input,
  OnInit,
  signal,
} from '@angular/core';
import * as L from 'leaflet';
import { Itinerary } from '../../models/itinerary';
import { HeatmapPoint } from '../../models/heatmap-point';
declare const HeatmapOverlay: any;

@Component({
  selector: 'app-map',
  imports: [],
  templateUrl: './map.html',
  styleUrl: './map.css',
})
export class Map implements OnInit, AfterViewInit {
  //
  //   Constants
  //
  
  private static readonly CITY_POINT: L.LatLngTuple = [40.71, -74];
  private static readonly CITY_ORIGINAL_ZOOM = 11;

  private static readonly HEAT_MAP_MAX_INTENSITY = 5;
  private static readonly POINTS_RADIUS = 0.004;

  private static readonly ITINERARY_COLOR = 'blue';
  private static readonly ITINERARY_WEIGHT = 2;
  private static readonly ITINERARY_OPACITY = 0.8;

  private static readonly PING_ICON = L.icon({
    iconUrl: 'images/ping.png',
    iconSize: [21, 21],
    iconAnchor: [21/2+1, 21],
    popupAnchor: [0, -21]
  });

  //
  //   Interfaces
  //
  
  public readonly itineraryData = input<Itinerary[]>([]);
  public readonly heatMapData = input<HeatmapPoint[]>([]);

  //
  //   Fields
  //
  
  private readonly map = signal<L.Map | null>(null);
  private readonly heatmapLayer = signal<typeof HeatmapOverlay | null>(null);
  private markers: L.Marker[] = [];
  private polylines: L.Polyline[] = [];
  
  //
  //   Init
  //
  
  public ngOnInit(): void {
    this.map.set(L.map("map").setView(Map.CITY_POINT, Map.CITY_ORIGINAL_ZOOM));
  
    const map = this.map();

    if (map) {
      // Settings the default map http location and default zoom
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19
      }).addTo(map);

      // Setting up the heatmap layer
      this.heatmapLayer.set(new HeatmapOverlay({
        radius: Map.POINTS_RADIUS,
        maxOpacity: 0.8,
        scaleRadius: true,
        useLocalExtrema: false,
        latField: 'lat',
        lngField: 'lng',
        valueField: 'count'
      }));

      // Adding the legend to the map
      const legend = new L.Control({ position: 'bottomright' });

        legend.onAdd = function () {
          const div = L.DomUtil.create('div', 'heatmap-legend');

          div.innerHTML =
            '<h2 class="legend-title">Accidents</h2>' +
            '<div class="legend-scale">' +
              '<span class="legend-min">1</span>' +
              '<div class="legend-bar"></div>' +
              '<span class="legend-max">' + Map.HEAT_MAP_MAX_INTENSITY + '</span>' +
            '</div>';

          return div;
        };

        legend.addTo(map);
    }
  }

  public ngAfterViewInit(): void {
    setTimeout(() => {
      const m = this.map();
      if (m) {
        m.invalidateSize();
      }
    }, 0);
  }
  
  //
  //   Effect
  //
  
  protected readonly mapDataEffect = effect(() => {

    const map = this.map();

    if (map) {
      // If there is itinerary data, add the itinerary to the map
      if (this.itineraryData()) {
        this.removeMarkersAndPolylines();

        this.itineraryData().forEach(itinerary => {

          // Adding a ping on both ends of the itinerary
          const startMarker = L.marker(itinerary.positions[0], {
            icon: Map.PING_ICON
          }).addTo(map).bindPopup(itinerary.popup_text ?? 'Start Point');

          const endMarker = L.marker(itinerary.positions[1], {
            icon: Map.PING_ICON
          }).addTo(map).bindPopup(itinerary.popup_text ?? 'End Point');

          // Adding the itinerary to the map
          const polyline = L.polyline(itinerary.positions, {
            color: itinerary.color ?? Map.ITINERARY_COLOR,
            weight: Map.ITINERARY_WEIGHT,
            opacity: Map.ITINERARY_OPACITY
          }).addTo(map);

          this.markers.push(startMarker, endMarker);
          this.polylines.push(polyline);
        });
      }

      const heatmapLayer = this.heatmapLayer();

      // If there is heat map data, add the heat map to the map
      if (heatmapLayer && this.heatMapData()) {

        heatmapLayer.addTo(map);

        const testData = {
          max: Map.HEAT_MAP_MAX_INTENSITY,
          data: this.heatMapData()
        };

        heatmapLayer.setData(testData);
      }
    }
  });

  //
  //   Methods
  //
  
  private removeMarkersAndPolylines(): void {
    this.markers.forEach(marker => marker.remove());
    this.polylines.forEach(polyline => polyline.remove());
    this.markers = [];
    this.polylines = [];
  }
}
