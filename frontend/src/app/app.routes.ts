import { Routes } from '@angular/router';

import { AddPageComponent } from './pages/add-page/add-page.component';
import { AskPageComponent } from './pages/ask-page/ask-page.component';
import { SourcesPageComponent } from './pages/sources-page/sources-page.component';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'sources',
  },
  {
    path: 'sources',
    component: SourcesPageComponent,
  },
  {
    path: 'add',
    component: AddPageComponent,
  },
  {
    path: 'ask',
    component: AskPageComponent,
  },
];
