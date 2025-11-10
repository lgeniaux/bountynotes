import { Component } from '@angular/core';

@Component({
  selector: 'app-sources-page',
  template: `
    <div class="page-copy">
      <p class="page-kicker">Sources</p>
      <h2>Source library landing page</h2>
      <p>
        This page will host the source list, filters, and status overview in the next frontend
        slice.
      </p>
    </div>
  `,
  styles: `
    .page-copy {
      max-width: 640px;
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
      margin: 0 0 12px;
      font-size: 1.875rem;
      line-height: 1.2;
      font-weight: 600;
      color: #111827;
    }

    p {
      margin: 0;
      max-width: 56ch;
      font-size: 1rem;
      line-height: 1.65;
      color: #4b5563;
    }
  `,
})
export class SourcesPageComponent {}
