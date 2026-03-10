import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HeatmapPoint } from '../models/heatmap-point';
import { AsyncHttpClient } from './async-http-client';

@Injectable({
  providedIn: 'root',
})
export class AccidentsService {
  //
  //   Interfaces
  //
  
  private readonly async_http_client = inject(AsyncHttpClient);

  //
  //   Methods
  //

  public getHeatmapData(): Observable<HeatmapPoint[]> {
    return this.async_http_client.get<HeatmapPoint[]>('/accidents/heatmap');
  }
}
