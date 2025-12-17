import { Component, EventEmitter, Input, Output } from '@angular/core';

import { AddMode } from '../../pages/add-page/add-mode';

@Component({
  selector: 'app-add-source-mode-switch',
  templateUrl: './add-source-mode-switch.component.html',
  styleUrl: './add-source-mode-switch.component.css',
})
export class AddSourceModeSwitchComponent {
  @Input({ required: true }) selectedMode: AddMode = 'url';
  @Input({ required: true }) disabled = false;

  @Output() modeChange = new EventEmitter<AddMode>();
}
