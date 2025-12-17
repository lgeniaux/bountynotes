import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';

import { AddMode } from './add-mode';
import { AddManualFormComponent } from '../../sources/add-manual-form/add-manual-form.component';
import { AddSourceModeSwitchComponent } from '../../sources/add-source-mode-switch/add-source-mode-switch.component';
import { AddUrlFormComponent } from '../../sources/add-url-form/add-url-form.component';
import { SourceRead } from '../../sources/source-read';
import { SourceCreateFeedbackComponent } from '../../sources/source-create-feedback/source-create-feedback.component';
import { SourcesApiService } from '../../sources/sources-api.service';

@Component({
  selector: 'app-add-page',
  imports: [
    AddManualFormComponent,
    AddSourceModeSwitchComponent,
    AddUrlFormComponent,
    SourceCreateFeedbackComponent,
  ],
  templateUrl: './add-page.component.html',
  styleUrl: './add-page.component.css',
})
export class AddPageComponent {
  private readonly formBuilder = inject(FormBuilder);
  private readonly sourcesApi = inject(SourcesApiService);

  protected readonly manualForm = this.formBuilder.group({
    title: this.formBuilder.control('', [Validators.maxLength(255)]),
    raw_content: this.formBuilder.control('', [Validators.required]),
  });

  protected readonly urlForm = this.formBuilder.group({
    title: this.formBuilder.control('', [Validators.maxLength(255)]),
    url: this.formBuilder.control('', [Validators.required, Validators.maxLength(2048)]),
  });

  protected selectedMode: AddMode = 'url';
  protected isSubmitting = false;
  protected errorMessage: string | null = null;
  protected createdSource: SourceRead | null = null;

  protected selectMode(mode: AddMode): void {
    if (this.selectedMode === mode || this.isSubmitting) {
      return;
    }

    this.selectedMode = mode;
    this.resetFeedback();
  }

  protected submitSource(): void {
    if (this.selectedMode === 'manual') {
      this.submitManualSource();
      return;
    }

    this.submitUrlSource();
  }

  protected get submitLabel(): string {
    return this.isSubmitting ? 'Adding...' : 'Add source';
  }

  private submitManualSource(): void {
    if (this.manualForm.invalid || this.isSubmitting) {
      this.manualForm.markAllAsTouched();
      return;
    }

    const title = this.manualForm.controls.title.value?.trim() ?? '';
    const rawContent = this.manualForm.controls.raw_content.value?.trim() ?? '';

    if (!rawContent) {
      this.manualForm.controls.raw_content.setErrors({ required: true });
      this.manualForm.controls.raw_content.markAsTouched();
      return;
    }

    this.beginSubmission();

    this.sourcesApi
      .createManualSource({
        title: title || null,
        raw_content: rawContent,
      })
      .subscribe({
        next: (source) => {
          this.manualForm.reset({ title: '', raw_content: '' });
          this.finishSubmissionSuccess(source);
        },
        error: (error: unknown) => {
          this.finishSubmissionError(error);
        },
      });
  }

  private submitUrlSource(): void {
    if (this.urlForm.invalid || this.isSubmitting) {
      this.urlForm.markAllAsTouched();
      return;
    }

    const title = this.urlForm.controls.title.value?.trim() ?? '';
    const url = this.urlForm.controls.url.value?.trim() ?? '';

    if (!url) {
      this.urlForm.controls.url.setErrors({ required: true });
      this.urlForm.controls.url.markAsTouched();
      return;
    }

    this.beginSubmission();

    this.sourcesApi
      .createUrlSource({
        title: title || null,
        url,
      })
      .subscribe({
        next: (source) => {
          this.urlForm.reset({ title: '', url: '' });
          this.finishSubmissionSuccess(source);
        },
        error: (error: unknown) => {
          this.finishSubmissionError(error);
        },
      });
  }

  private beginSubmission(): void {
    this.isSubmitting = true;
    this.resetFeedback();
  }

  private finishSubmissionSuccess(source: SourceRead): void {
    this.createdSource = source;
    this.isSubmitting = false;
  }

  private finishSubmissionError(error: unknown): void {
    this.errorMessage = this.getErrorMessage(error);
    this.isSubmitting = false;
  }

  private resetFeedback(): void {
    this.errorMessage = null;
    this.createdSource = null;
  }

  private getErrorMessage(error: unknown): string {
    if (error instanceof HttpErrorResponse) {
      const detail = error.error?.detail;

      if (typeof detail === 'string' && detail.trim()) {
        return detail;
      }
    }

    return 'Could not add the source. Make sure the API is running.';
  }
}
