import { Injectable } from '@angular/core';
import { Observable, delay, of } from 'rxjs';

import { AskRequest } from './ask-request';
import { AskResponse } from './ask-response';
import { MOCK_ASK_RESPONSE } from './mock-ask-response';

@Injectable({
  providedIn: 'root',
})
export class AskApiService {
  ask(payload: AskRequest): Observable<AskResponse> {
    const query = payload.query.trim();
    const answer = query
      ? `Temporary mock answer for "${query}". ${MOCK_ASK_RESPONSE.answer}`
      : MOCK_ASK_RESPONSE.answer;

    return of({
      ...MOCK_ASK_RESPONSE,
      answer,
      citations: [...MOCK_ASK_RESPONSE.citations],
    }).pipe(delay(250));
  }
}
