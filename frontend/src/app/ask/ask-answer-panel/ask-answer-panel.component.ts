import { Component, Input } from '@angular/core';

import { AskResponse } from '../ask-response';
import { CitationListComponent } from '../citation-list/citation-list.component';

@Component({
  selector: 'app-ask-answer-panel',
  imports: [CitationListComponent],
  templateUrl: './ask-answer-panel.component.html',
  styleUrl: './ask-answer-panel.component.css',
})
export class AskAnswerPanelComponent {
  @Input({ required: true }) query = '';
  @Input({ required: true }) response!: AskResponse;
}
