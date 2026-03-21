import { effect, inject, Injectable, signal } from '@angular/core';
import { AsyncHttpClient } from './async-http-client';
import { BehaviorSubject, map, Observable, switchMap, tap } from 'rxjs';
import { ChartData, ChartDataSchema } from '../models/chart-data';
import { toSignal } from '@angular/core/rxjs-interop';
import { Itinerary } from '../models/itinerary';

/**
 * MAI as Most Accidented Itineraries Service.
 */
@Injectable({
  providedIn: 'root',
})
export class MaiService {
  //
  //   Constants
  //
  
  private readonly TITLE = ['Accidents'];
  private readonly COLORS = ['rgba(249, 115, 22, 0.2)', 'rgba(6, 182, 212, 0.2)', 'rgb(107, 114, 128, 0.2)', 'rgba(139, 92, 246, 0.2)', 'rgba(81, 7, 255, 0.2)'];
  private readonly BORDER_COLORS = ['rgba(249, 115, 22)', 'rgba(6, 182, 212)', 'rgb(107, 114, 128)', 'rgba(139, 92, 246)', 'rgba(81, 7, 255)'];

  //
  //   Interfaces
  //
  
  private readonly async_http_client = inject(AsyncHttpClient);

  //
  //   Forms
  //
  
  public readonly topN = signal<number>(5);
  public readonly dateFrom = signal<Date | null>(null);
  public readonly dateTo = signal<Date | null>(null);
  public readonly bikeAccType = signal<string | null>(null);

  //
  //   Effects
  //
  
  protected readonly topNEffect = effect(() => {
    if (this.topN() < 1 || this.topN() > 20) {
      setTimeout(() => {
        this.topN.set(5);
      }, 100);
    }
    this.refresh();
  });

  //
  //   Methods
  //

  public getTopNAccidentedItineraries(): Observable<Itinerary[]> {
    //
    //   Preparing the query parameters
    //
    
    const params: Record<string, any> = {
      n: this.topN(),
    };
    if (this.dateFrom()) {
      params['date_from'] = this.dateFrom()!.toISOString().slice(0, 10);
    }
    if (this.dateTo()) {
      params['date_to'] = this.dateTo()!.toISOString().slice(0, 10);
    }
    if (this.bikeAccType()) {
      params['bike_acc_type'] = this.bikeAccType();
    }

    //
    //   Processing the received data
    //
    return this.async_http_client.get<Itinerary[]>('/mai/topn', params);
  }

  //
  //   Refrashable data
  //
  
  private readonly refreshTrigger = new BehaviorSubject<void>(undefined);

  public refresh(): void {
    this.refreshTrigger.next();
  }

  public topNAccidentedItinerariesChart = toSignal<ChartData>(this.refreshTrigger.pipe(
    switchMap(() => this.getTopNAccidentedItineraries()),
    map((itineraries) => {
      let index = -1;
      return ChartDataSchema.parse({
        labels: this.TITLE,
        datasets: itineraries.map((itinerary) => {
            index++;     
            return {
              label: `${itinerary.start_station_name} => ${itinerary.end_station_name}`,
              data: [itinerary.nb_acc],
              backgroundColor: [this.COLORS[index % this.COLORS.length]],
              borderColor: [this.BORDER_COLORS[index % this.BORDER_COLORS.length]],
              borderWidth: 1,
            }
        }),
      });
    })
  ));

  public topNAccidentedItineraries = toSignal<Itinerary[]>(
    this.refreshTrigger.pipe(
      switchMap(() => this.getTopNAccidentedItineraries())
    )
  );
}
