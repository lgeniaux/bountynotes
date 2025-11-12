import { DatePipe, TitleCasePipe } from '@angular/common';
import { Component, Input } from '@angular/core';

import { SourceListItem } from './source-list-item';

@Component({
  selector: 'app-source-card',
  imports: [DatePipe, TitleCasePipe],
  templateUrl: './source-card.component.html',
  styleUrl: './source-card.component.css',
})
export class SourceCardComponent {
  @Input({ required: true }) source!: SourceListItem;
}
