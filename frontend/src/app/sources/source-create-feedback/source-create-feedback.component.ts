import { Component, Input } from '@angular/core';
import { RouterLink } from '@angular/router';

import { SourceRead } from '../source-read';

@Component({
  selector: 'app-source-create-feedback',
  imports: [RouterLink],
  templateUrl: './source-create-feedback.component.html',
  styleUrl: './source-create-feedback.component.css',
})
export class SourceCreateFeedbackComponent {
  @Input() createdSource: SourceRead | null = null;
  @Input() errorMessage: string | null = null;
}
