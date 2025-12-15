import { Component, Input } from '@angular/core';

import { AskCitation } from '../ask-citation';
import { PageStateCardComponent } from '../../shared/page-state-card/page-state-card.component';

@Component({
  selector: 'app-citation-list',
  imports: [PageStateCardComponent],
  templateUrl: './citation-list.component.html',
  styleUrl: './citation-list.component.css',
})
export class CitationListComponent {
  @Input({ required: true }) citations: AskCitation[] = [];
}
