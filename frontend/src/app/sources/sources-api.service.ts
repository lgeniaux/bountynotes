import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../core/api-base-url';
import { SourceListItem } from './source-list-item';
import { SourceManualCreatePayload } from './source-manual-create-payload';
import { SourceRead } from './source-read';
import { SourceUrlCreatePayload } from './source-url-create-payload';

@Injectable({
  providedIn: 'root',
})
export class SourcesApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = inject(API_BASE_URL);

  listSources(): Observable<SourceListItem[]> {
    return this.http.get<SourceListItem[]>(`${this.apiBaseUrl}/sources`);
  }

  createManualSource(payload: SourceManualCreatePayload): Observable<SourceRead> {
    return this.http.post<SourceRead>(`${this.apiBaseUrl}/sources/manual`, payload);
  }

  createUrlSource(payload: SourceUrlCreatePayload): Observable<SourceRead> {
    return this.http.post<SourceRead>(`${this.apiBaseUrl}/sources/url`, payload);
  }
}
