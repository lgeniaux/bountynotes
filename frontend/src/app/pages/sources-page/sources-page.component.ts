import { AsyncPipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { catchError, map, Observable, of, startWith } from 'rxjs';

import { PageStateCardComponent } from '../../shared/page-state-card/page-state-card.component';
import { SourceListItem } from '../../sources/source-list-item';
import { SourceCardComponent } from '../../sources/source-card/source-card.component';
import { SourcesApiService } from '../../sources/sources-api.service';

interface SourcesPageState {
  sources: SourceListItem[];
  isLoading: boolean;
  errorMessage: string | null;
}

@Component({
  selector: 'app-sources-page',
  imports: [AsyncPipe, RouterLink, PageStateCardComponent, SourceCardComponent],
  templateUrl: './sources-page.component.html',
  styleUrl: './sources-page.component.css',
})
export class SourcesPageComponent {
  private readonly sourcesApi = inject(SourcesApiService);

  protected readonly state$: Observable<SourcesPageState> = this.sourcesApi.listSources().pipe(
    map((sources) => ({
      sources,
      isLoading: false,
      errorMessage: null,
    })),
    catchError(() =>
      of({
        sources: [],
        isLoading: false,
        errorMessage: 'Make sure the API is running and reachable from the web app.',
      }),
    ),
    startWith({
      sources: [],
      isLoading: true,
      errorMessage: null,
    }),
  );
}
