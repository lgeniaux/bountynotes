import { DatePipe, TitleCasePipe } from '@angular/common';
import { Component, Input } from '@angular/core';

import { SourceListItem } from './source-list-item';
import { SourceStatus } from './source-status';

@Component({
  selector: 'app-source-card',
  imports: [DatePipe, TitleCasePipe],
  templateUrl: './source-card.component.html',
  styleUrl: './source-card.component.css',
})
export class SourceCardComponent {
  @Input({ required: true }) source!: SourceListItem;

  protected readonly statusLabels: Record<SourceStatus, string> = {
    pending: 'Pending',
    processing: 'Processing',
    ready: 'Ready',
    failed: 'Failed',
  };

  protected getStatusDescription(source: SourceListItem): string {
    switch (source.status) {
      case 'pending':
        return 'Waiting for background processing to start.';
      case 'processing':
        return 'Content is being cleaned and prepared for retrieval.';
      case 'ready':
        return 'This source is ready to support answers in Ask.';
      case 'failed':
        return 'Processing failed. Review the error details before retrying.';
    }
  }
}
