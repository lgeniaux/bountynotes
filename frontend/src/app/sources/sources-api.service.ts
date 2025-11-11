import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../core/api-base-url';
import { SourceListItem } from './source-list-item';

@Injectable({
  providedIn: 'root',
})
export class SourcesApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = inject(API_BASE_URL);

  listSources(): Observable<SourceListItem[]> {
    return this.http.get<SourceListItem[]>(`${this.apiBaseUrl}/sources`);
  }
}
