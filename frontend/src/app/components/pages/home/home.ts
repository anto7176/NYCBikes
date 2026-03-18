import { Component, effect, inject, signal } from '@angular/core';
import { Map } from '../../map/map';
import { UploadZone } from '../../upload-zone/upload-zone';
import { AccidentsService } from '../../../services/accidents-service';
import { HeatmapPoint } from '../../../models/heatmap-point';
import { DatePicker } from 'primeng/datepicker';
import { FormsModule } from '@angular/forms';
import { FloatLabelModule } from 'primeng/floatlabel';
import { Chart } from '../../chart/chart';

@Component({
  selector: 'app-home',
  imports: [
    Map,
    UploadZone,
    DatePicker,
    FormsModule,
    FloatLabelModule,
    Chart
  ],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home {
  //
  //   Interfaces
  //

  protected readonly accidentsService = inject(AccidentsService);

  //
  //   Data
  //
  
  protected readonly heatMapData = signal<HeatmapPoint[]>([]);

  //
  //   Forms
  //
  
  protected readonly dateFrom = signal<Date | null>(null);
  protected readonly dateTo = signal<Date | null>(null);

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
