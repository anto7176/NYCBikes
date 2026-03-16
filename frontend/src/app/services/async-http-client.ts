import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AsyncHttpClient {
  //
  //   Interfaces
  //

  private readonly http_client = inject(HttpClient)

  //
  //   Fields
  //

  private readonly apiUrl = AsyncHttpClient.stripEndSlash(
    environment.apiBaseUrl
  )

  //
  //   Methods
  //

  public prepareUrl(endpoint: string): string {
    return this.apiUrl + "/" + AsyncHttpClient.stripStartSlash(endpoint);
  }

  public get<T>(
    endpoint: string,
    queryParams?: Record<string, any>,
  ): Observable<T> {
    return this.http_client.get<T>(
      this.prepareUrl(endpoint),
      {
        params: queryParams
      }
    )
  }

  public post<T>({ endpoint, json, data} : {
    endpoint: string,
    json?: Record<string, any> | any[],
    data?: FormData
  }): Observable<T> {
    if (json && data) {
      throw new Error("Cannot send form data and json at the same time");
    }


    return this.http_client.post<T>(
      this.prepareUrl(endpoint),
      json ?? data
    )
  }

  public put<T>({ endpoint, json, data} : {
    endpoint: string,
    json?: Record<string, any>,
    data?: FormData
  }): Observable<T> {
    return this.http_client.put<T>(
      this.prepareUrl(endpoint),
      json ?? data
    )
  }

  public delete<T>(endpoint: string): Observable<T> {
    return this.http_client.delete<T>(
      this.prepareUrl(endpoint)
    );
  }

  //
  //   Statis functions
  //

  public static stripStartSlash(str: string): string {
    return str.startsWith("/") ? str.slice(1) : str;
  }

  public static stripEndSlash(str: string): string {
    return str.endsWith("/") ? str.slice(0, -1) : str;
  }
}
