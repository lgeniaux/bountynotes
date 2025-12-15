import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';

import { SourceListItem } from '../../sources/source-list-item';

type AskFilterPanel = 'source' | 'tags' | 'cwes' | 'cves' | null;
type AskTextFilterControlName = 'tags_text' | 'cwes_text' | 'cves_text';

@Component({
  selector: 'app-ask-filter-panel',
  imports: [ReactiveFormsModule],
  templateUrl: './ask-filter-panel.component.html',
  styleUrl: './ask-filter-panel.component.css',
})
export class AskFilterPanelComponent {
  @Input({ required: true }) activePanel: AskFilterPanel = null;
  @Input({ required: true }) sources: SourceListItem[] = [];
  @Input({ required: true }) isSourceLoading = false;
  @Input({ required: true }) sourceErrorMessage: string | null = null;
  @Input({ required: true }) sourceIdControl!: FormControl<number | null>;
  @Input({ required: true }) tagsControl!: FormControl<string | null>;
  @Input({ required: true }) cwesControl!: FormControl<string | null>;
  @Input({ required: true }) cvesControl!: FormControl<string | null>;

  @Output() clearSource = new EventEmitter<void>();
  @Output() clearTextFilter = new EventEmitter<AskTextFilterControlName>();
}
