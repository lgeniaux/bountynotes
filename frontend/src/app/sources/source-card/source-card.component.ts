import { DatePipe } from '@angular/common';
import { Component, Input } from '@angular/core';

import { SourceListItem } from '../source-list-item';
import { SourceStatus } from '../source-status';

@Component({
  selector: 'app-source-card',
  imports: [DatePipe],
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

  protected readonly sourceTypeLabels: Record<string, string> = {
    manual: 'Manual note',
    url: 'URL source',
  };

  protected getStatusDescription(source: SourceListItem): string {
    switch (source.status) {
      case 'pending':
        return 'Waiting for processing to start.';
      case 'processing':
        return 'Content is being prepared for Ask.';
      case 'ready':
        return 'Ready for Ask.';
      case 'failed':
        return 'Processing failed.';
    }
  }

  protected getSourceTypeLabel(source: SourceListItem): string {
    return this.sourceTypeLabels[source.source_type] ?? source.source_type;
  }
}
