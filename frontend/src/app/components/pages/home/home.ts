import { Component, computed, effect, inject, signal } from '@angular/core';
import { Map } from '../../map/map';
import { UploadZone } from '../../upload-zone/upload-zone';
import { AccidentsService } from '../../../services/accidents-service';
import { HeatmapPoint } from '../../../models/heatmap-point';
import { DatePicker } from 'primeng/datepicker';
import { FormsModule } from '@angular/forms';
import { FloatLabelModule } from 'primeng/floatlabel';
import { Chart } from '../../chart/chart';
import { MaiService } from '../../../services/mai-service';
import { SelectModule } from 'primeng/select';
import { InputNumberModule } from 'primeng/inputnumber';

@Component({
  selector: 'app-home',
  imports: [
    Map,
    UploadZone,
    DatePicker,
    FormsModule,
    FloatLabelModule,
    Chart,
    SelectModule,
    InputNumberModule,
  ],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home {
  //
  //   Interfaces
  //

  protected readonly accidentsService = inject(AccidentsService);
  protected readonly maiService = inject(MaiService);

  //
  //   Data
  //
  
  protected readonly heatMapData = signal<HeatmapPoint[]>([]);
  protected readonly itineraryTypes = signal<{ label: string, value: string }[]>([
    { label: 'Bikes itinerary', value: 'bikes_itinerary' },
    { label: 'Top n accidented itineraries', value: 'accidented_itineraries' },
  ]);

  //
  //   Forms
  //
  
  protected readonly dateFrom = signal<Date | null>(null);
  protected readonly dateTo = signal<Date | null>(null);
  protected readonly selectedItineraryType = signal<string>('accidented_itineraries');

  //
  //   Computed values
  //
  
  /**
   * Gets the itineraries to display on the map according to
   * the user selection : selectedItineraryType.
   */
  protected readonly itineraryData = computed(() => {
    if (this.selectedItineraryType() === 'accidented_itineraries') {
      return this.maiService.topNAccidentedItineraries();
    } else if (this.selectedItineraryType() === 'bikes_itinerary') {
      // return this.maiService.getBikesItinerary();
    }
    return [];
  });

  //
  //   Effects
  //
  
  protected readonly heatMapDataEffect = effect(() => {

    // Getting the heatmap data from the backend
    this.accidentsService.getHeatmapData(
      this.dateFrom(),
      this.dateTo()
    ).subscribe(data => {

      // Pushing the new data to the signal and forcing update
      this.heatMapData.set(data);
    });

  });
}
