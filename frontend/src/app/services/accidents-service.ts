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

  public getHeatmapData(dateFrom: Date | null, dateTo: Date | null): Observable<HeatmapPoint[]> {
    const params: Record<string, any> = {};
    if (dateFrom) {
      params['date_from'] = dateFrom.toISOString().slice(0, 10);
    }
    if (dateTo) {
      params['date_to'] = dateTo.toISOString().slice(0, 10);
    }
    
    return this.async_http_client.get<HeatmapPoint[]>('/accidents/heatmap', 
      params
    );
  }
}
