import { Component } from '@angular/core';

@Component({
  selector: 'app-ask-page',
  template: `
    <div class="page-copy">
      <p class="page-kicker">Ask</p>
      <h2>Question and citation workspace</h2>
      <p>
        This page will host the ask flow, filters, final answer, and citations once the backend is
        ready.
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
export class AskPageComponent {}
