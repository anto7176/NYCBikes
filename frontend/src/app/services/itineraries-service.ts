import { inject, Injectable } from '@angular/core';
import { AsyncHttpClient } from './async-http-client';
import { BehaviorSubject, map, Observable, switchMap } from 'rxjs';
import { toSignal } from '@angular/core/rxjs-interop';
import { Itinerary } from '../models/itinerary';

@Injectable({
  providedIn: 'root',
})
export class ItinerariesService {
  //
  //   Interfaces
  //
  
  private readonly async_http_client = inject(AsyncHttpClient);

  //
  //   Methods
  //

  // 1. Pour les Top Itineraries (on les transforme en Itinerary classique pour tracer les lignes)
  public getTopItineraries(): Observable<Itinerary[]> {
    return this.async_http_client.get<any[]>('/itineraries/TopItinerary').pipe(
      map(data => data.map(item => ({
        positions: [
          [item.start_lat, item.start_lng],
          [item.end_lat, item.end_lng]
        ],
        popup_text: `Count: ${item.count}`,
        color: '#10b981' // Une couleur verte par exemple pour les différencier
      } as Itinerary)))
    );
  }


  //
  //   Refreshable data (Même mécanique que ton mai-service)
  //
  
  private readonly refreshTrigger = new BehaviorSubject<void>(undefined);

  public refresh(): void {
    this.refreshTrigger.next();
  }

  public topItineraries = toSignal<Itinerary[]>(
    this.refreshTrigger.pipe(
      switchMap(() => this.getTopItineraries())
    )
  );
}