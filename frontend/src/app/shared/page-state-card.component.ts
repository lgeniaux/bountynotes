import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-page-state-card',
  templateUrl: './page-state-card.component.html',
  styleUrl: './page-state-card.component.css',
})
export class PageStateCardComponent {
  @Input({ required: true }) title!: string;
  @Input({ required: true }) message!: string;
  @Input() tone: 'default' | 'error' = 'default';
}
