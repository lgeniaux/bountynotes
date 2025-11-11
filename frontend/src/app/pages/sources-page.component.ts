import { Component, OnInit, inject } from '@angular/core';

import { SourceListItem } from '../sources/source-list-item';
import { SourcesApiService } from '../sources/sources-api.service';

@Component({
  selector: 'app-sources-page',
  template: `
    <section class="sources-page">
      <header class="sources-header">
        <div>
          <p class="page-kicker">Sources</p>
          <h2>Source library</h2>
        </div>
        <p class="sources-count">{{ sources.length }} total</p>
      </header>

      <p class="page-intro">
        Review the current source set before adding new write-ups or moving to the ask flow.
      </p>

      @if (isLoading) {
        <div class="state-card">
          <h3>Loading sources</h3>
          <p>The page is requesting the latest source list from the API.</p>
        </div>
      } @else if (errorMessage) {
        <div class="state-card state-card-error">
          <h3>Could not load sources</h3>
          <p>{{ errorMessage }}</p>
        </div>
      } @else if (sources.length === 0) {
        <div class="state-card">
          <h3>No sources yet</h3>
          <p>Add a manual note or a URL source to start building the knowledge base.</p>
        </div>
      } @else {
        <div class="sources-list" aria-label="Sources list">
          @for (source of sources; track source.id) {
            <article class="source-card">
              <div class="source-card-header">
                <div>
                  <p class="source-meta">Source #{{ source.id }}</p>
                  <h3>{{ getDisplayTitle(source) }}</h3>
                </div>
                <div class="source-badges">
                  <span class="badge">{{ source.source_type }}</span>
                  <span class="badge badge-status">{{ source.status }}</span>
                </div>
              </div>

              <dl class="source-details">
                <div>
                  <dt>Created</dt>
                  <dd>{{ formatDate(source.created_at) }}</dd>
                </div>
                <div>
                  <dt>Updated</dt>
                  <dd>{{ formatDate(source.updated_at) }}</dd>
                </div>
              </dl>
            </article>
          }
        </div>
      }
    </section>
  `,
  styles: `
    .sources-page {
      display: grid;
      gap: 20px;
    }

    .page-kicker {
      margin: 0 0 8px;
      font-size: 0.8rem;
      font-weight: 600;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: #0369a1;
    }

    h2 {
      margin: 0;
      font-size: 1.875rem;
      line-height: 1.2;
      font-weight: 600;
      color: #111827;
    }

    h3 {
      margin: 0;
      font-size: 1.1rem;
      line-height: 1.35;
      color: #111827;
    }

    p {
      margin: 0;
      font-size: 1rem;
      line-height: 1.6;
      color: #4b5563;
    }

    .sources-header {
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 16px;
      padding-bottom: 16px;
      border-bottom: 1px solid #e5e7eb;
    }

    .sources-count {
      font-size: 0.95rem;
      color: #6b7280;
    }

    .page-intro {
      max-width: 62ch;
    }

    .state-card,
    .source-card {
      padding: 18px;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      background: #f9fafb;
    }

    .state-card {
      display: grid;
      gap: 8px;
      max-width: 720px;
    }

    .state-card-error {
      border-color: #fecaca;
      background: #fef2f2;
    }

    .sources-list {
      display: grid;
      gap: 14px;
    }

    .source-card {
      display: grid;
      gap: 16px;
      background: #ffffff;
    }

    .source-card-header {
      display: flex;
      align-items: start;
      justify-content: space-between;
      gap: 16px;
    }

    .source-meta {
      margin-bottom: 6px;
      font-size: 0.8rem;
      letter-spacing: 0.03em;
      text-transform: uppercase;
      color: #6b7280;
    }

    .source-badges {
      display: flex;
      flex-wrap: wrap;
      justify-content: end;
      gap: 8px;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 0 10px;
      border-radius: 999px;
      background: #e0f2fe;
      color: #075985;
      font-size: 0.85rem;
      font-weight: 600;
      text-transform: capitalize;
    }

    .badge-status {
      background: #e5e7eb;
      color: #374151;
    }

    .source-details {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin: 0;
    }

    .source-details div {
      padding-top: 12px;
      border-top: 1px solid #e5e7eb;
    }

    dt {
      margin: 0 0 4px;
      font-size: 0.8rem;
      font-weight: 600;
      letter-spacing: 0.03em;
      text-transform: uppercase;
      color: #6b7280;
    }

    dd {
      margin: 0;
      font-size: 0.95rem;
      color: #111827;
    }

    @media (max-width: 720px) {
      .sources-header,
      .source-card-header {
        flex-direction: column;
        align-items: stretch;
      }

      .source-badges {
        justify-content: start;
      }

      .source-details {
        grid-template-columns: 1fr;
      }
    }
  `,
})
export class SourcesPageComponent implements OnInit {
  private readonly sourcesApi = inject(SourcesApiService);
  private readonly dateFormatter = new Intl.DateTimeFormat('en', {
    dateStyle: 'medium',
    timeStyle: 'short',
  });

  protected sources: SourceListItem[] = [];
  protected isLoading = true;
  protected errorMessage: string | null = null;

  ngOnInit(): void {
    this.sourcesApi.listSources().subscribe({
      next: (sources) => {
        this.sources = sources;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'Make sure the API is running on http://localhost:8000.';
        this.isLoading = false;
      },
    });
  }

  protected getDisplayTitle(source: SourceListItem): string {
    return source.title?.trim() || 'Untitled source';
  }

  protected formatDate(value: string): string {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return value;
    }

    return this.dateFormatter.format(date);
  }
}
