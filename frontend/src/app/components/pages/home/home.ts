import { Component, inject, OnInit, signal } from '@angular/core';
import { Map } from '../../map/map';
import { UploadZone } from '../../upload-zone/upload-zone';
import { AccidentsService } from '../../../services/accidents-service';
import { HeatmapPoint } from '../../../models/heatmap-point';

@Component({
  selector: 'app-home',
  imports: [
    Map,
    UploadZone
  ],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home implements OnInit {
  //
  //   Interfaces
  //

  protected readonly accidentsService = inject(AccidentsService);

  //
  //   Data
  //
  
  protected readonly heatMapData = signal<HeatmapPoint[]>([]);

  //
  //   Init
  //
  
  ngOnInit(): void {

    this.accidentsService.getHeatmapData().subscribe(data => {
      this.heatMapData.set(data);
    });

  }
}
