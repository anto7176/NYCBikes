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
import { CheckboxModule } from 'primeng/checkbox';
import { Tooltip } from 'primeng/tooltip';
import { ItinerariesService } from '../../../services/itineraries-service';


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
    CheckboxModule,
    Tooltip,
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
  protected readonly itinerariesService = inject(ItinerariesService);

  //
  //   Constants
  //
  
  protected readonly BIKE_ACC_TYPES = [
    { label: 'Bikes Injured', value: "bikes_injured" },
    { label: 'Bikes Killed', value: "bikes_killed" },
  ];

  protected readonly tipBikesOnly =
    "Shows only bicycle-related accidents on the heatmap.";

  protected readonly tipBikeAccType =
    "Changing this reapplies a heavy server-side filter. The heatmap "
    + "can take up to about 15 seconds to refresh.";

  protected readonly tipDates =
    "Narrow the window to load less data. If start is after end, "
    + "both dates clear.";

  protected readonly tipItineraryType =
    "Switches overlays between bike itineraries and top accidented "
    + "corridors. Each change fetches new data.";

  protected readonly tipTopN =
    "How many worst corridors to show on the map and bar chart.";

  protected readonly tipHeatmapLoading =
    "Loading heatmap points from the server. This can take a few "
    + "seconds after a filter change.";

  protected readonly tipMap =
    "Drag to pan, scroll or +/- to zoom. Intensity follows the "
    + "heatmap legend scale.";

  protected readonly tipChart =
    "Uses the same date range and bike filters as the heatmap.";

  //
  //   Data
  //
  
  protected readonly heatMapData = signal<HeatmapPoint[]>([]);
  protected readonly itineraryTypes = signal<{ label: string, value: string }[]>([
    { label: 'Bikes itinerary', value: 'bikes_itinerary' },
    { label: 'Top n accidented itineraries', value: 'accidented_itineraries' },
    { label: 'Top itineraries', value: 'top_itineraries' }, 
  ]);

  //
  //   Forms
  //
  
  protected readonly dateFrom = signal<Date | null>(null);
  protected readonly dateTo = signal<Date | null>(null);
  protected readonly selectedItineraryType = signal<string>('accidented_itineraries');
  protected readonly bikesOnly = signal<boolean>(false);
  protected readonly bikeAccType = signal<string | null>(null);

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
    } else if (this.selectedItineraryType() === 'top_itineraries') {
      return this.itinerariesService.topItineraries(); // <-- ajout
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
      this.dateTo(),
      this.bikeAccType()
    ).subscribe(data => {

      // Pushing the new data to the signal and forcing update
      this.heatMapData.set(data);
    });

  });

  protected readonly datesEffect = effect(() => {
    const df = this.dateFrom();
    const dt = this.dateTo();

    if (df && dt && df > dt) {
      setTimeout(() => {
        this.dateFrom.set(null);
        this.dateTo.set(null);
      }, 10);
    }

    this.maiService.dateFrom.set(df);
    this.maiService.dateTo.set(dt);

    setTimeout(() => {
      this.maiService.refresh();
    }, 16);
  });

  protected readonly bikesOnlyEffect = effect(() => {
    if (this.bikesOnly() && !this.bikeAccType()) {
      this.bikeAccType.set("bikes_injured");
    }
    
    if (!this.bikesOnly() && this.bikeAccType()) {
      this.bikeAccType.set(null);
    }
  });

  protected readonly bikeAccTypeEffect = effect(() => {
    this.maiService.bikeAccType.set(this.bikeAccType());
  });
}
