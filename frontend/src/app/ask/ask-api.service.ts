import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../core/api-base-url';
import { AskRequest } from './ask-request';
import { AskResponse } from './ask-response';

@Injectable({
  providedIn: 'root',
})
export class AskApiService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = inject(API_BASE_URL);

  ask(payload: AskRequest): Observable<AskResponse> {
    return this.http.post<AskResponse>(`${this.apiBaseUrl}/ask`, payload);
  }
}
