import { Component, EventEmitter, Input, Output } from '@angular/core';

type AskFilterPanel = 'source' | 'tags' | 'cwes' | 'cves' | null;

@Component({
  selector: 'app-ask-filter-bar',
  templateUrl: './ask-filter-bar.component.html',
  styleUrl: './ask-filter-bar.component.css',
})
export class AskFilterBarComponent {
  @Input({ required: true }) activePanel: AskFilterPanel = null;
  @Input({ required: true }) isSourceSelected = false;
  @Input({ required: true }) isSourceLoading = false;
  @Input({ required: true }) sourceLabel = 'Source';
  @Input({ required: true }) tagsLabel = 'Tags';
  @Input({ required: true }) cwesLabel = 'CWEs';
  @Input({ required: true }) cvesLabel = 'CVEs';

  @Output() panelChange = new EventEmitter<Exclude<AskFilterPanel, null>>();

  protected openPanel(panel: Exclude<AskFilterPanel, null>): void {
    this.panelChange.emit(panel);
  }
}
