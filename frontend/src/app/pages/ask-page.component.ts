import { AsyncPipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { catchError, map, of, startWith } from 'rxjs';

import { AskApiService } from '../ask/ask-api.service';
import { AskResponse } from '../ask/ask-response';
import { PageStateCardComponent } from '../shared/page-state-card.component';
import { SourceListItem } from '../sources/source-list-item';
import { SourcesApiService } from '../sources/sources-api.service';

interface AskPageSourceState {
  sources: SourceListItem[];
  isLoading: boolean;
  errorMessage: string | null;
}

@Component({
  selector: 'app-ask-page',
  imports: [AsyncPipe, PageStateCardComponent, ReactiveFormsModule],
  templateUrl: './ask-page.component.html',
  styleUrl: './ask-page.component.css',
})
export class AskPageComponent {
  private readonly formBuilder = inject(FormBuilder);
  private readonly askApi = inject(AskApiService);
  private readonly sourcesApi = inject(SourcesApiService);

  protected readonly askForm = this.formBuilder.group({
    query: this.formBuilder.control('', [Validators.required]),
    tags_text: this.formBuilder.control(''),
    cwes_text: this.formBuilder.control(''),
    cves_text: this.formBuilder.control(''),
    source_id: this.formBuilder.control<number | null>(null),
  });

  protected isSubmitting = false;
  protected askErrorMessage: string | null = null;
  protected response: AskResponse | null = null;

  protected readonly sourceState$ = this.sourcesApi.listSources().pipe(
    map((sources) => ({
      sources: sources.filter((source) => source.status === 'ready'),
      isLoading: false,
      errorMessage: null,
    })),
    catchError(() =>
      of({
        sources: [],
        isLoading: false,
        errorMessage: 'Could not load sources from the API. Filters stay unavailable for now.',
      }),
    ),
    startWith({
      sources: [],
      isLoading: true,
      errorMessage: null,
    }),
  );

  protected submitAsk(): void {
    if (this.askForm.invalid || this.isSubmitting) {
      this.askForm.markAllAsTouched();
      return;
    }

    const query = this.askForm.controls.query.value?.trim() ?? '';

    if (!query) {
      this.askForm.controls.query.setErrors({ required: true });
      this.askForm.controls.query.markAsTouched();
      return;
    }

    this.isSubmitting = true;
    this.askErrorMessage = null;
    this.response = null;

    this.askApi
      .ask({
        query,
        filters: this.buildFilters(),
      })
      .subscribe({
        next: (response) => {
          this.response = response;
          this.isSubmitting = false;
        },
        error: () => {
          this.askErrorMessage = 'Could not generate an answer right now.';
          this.isSubmitting = false;
        },
      });
  }

  protected hasControlError(
    controlName: 'query' | 'tags_text' | 'cwes_text' | 'cves_text',
    errorCode: string,
  ): boolean {
    const control = this.askForm.controls[controlName];
    return !!control.errors?.[errorCode] && (control.touched || control.dirty);
  }

  protected isSourceSelected(sourceId: number): boolean {
    return this.askForm.controls.source_id.value === sourceId;
  }

  protected toggleSourceSelection(sourceId: number, isSelected: boolean): void {
    if (isSelected) {
      this.askForm.controls.source_id.setValue(sourceId);
      return;
    }

    if (this.askForm.controls.source_id.value === sourceId) {
      this.askForm.controls.source_id.setValue(null);
    }
  }

  private buildFilters() {
    const filters = {
      source_id: this.askForm.controls.source_id.value,
      tags: this.parseFilterList(this.askForm.controls.tags_text.value),
      cwes: this.parseFilterList(this.askForm.controls.cwes_text.value),
      cves: this.parseFilterList(this.askForm.controls.cves_text.value),
    };

    if (
      !filters.source_id &&
      filters.tags.length === 0 &&
      filters.cwes.length === 0 &&
      filters.cves.length === 0
    ) {
      return null;
    }

    return filters;
  }

  private parseFilterList(value: string | null | undefined): string[] {
    return (value ?? '')
      .split(',')
      .map((item) => item.trim())
      .filter((item) => item.length > 0);
  }
}
