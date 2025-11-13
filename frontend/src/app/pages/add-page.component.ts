import { HttpErrorResponse } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { SourceRead } from '../sources/source-read';
import { SourcesApiService } from '../sources/sources-api.service';

@Component({
  selector: 'app-add-page',
  imports: [ReactiveFormsModule, RouterLink],
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

  protected isManualSubmitting = false;
  protected manualErrorMessage: string | null = null;
  protected createdManualSource: SourceRead | null = null;

  protected isUrlSubmitting = false;
  protected urlErrorMessage: string | null = null;
  protected createdUrlSource: SourceRead | null = null;

  protected submitManualSource(): void {
    if (this.manualForm.invalid || this.isManualSubmitting) {
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

    this.isManualSubmitting = true;
    this.manualErrorMessage = null;
    this.createdManualSource = null;

    this.sourcesApi
      .createManualSource({
        title: title || null,
        raw_content: rawContent,
      })
      .subscribe({
        next: (source) => {
          this.createdManualSource = source;
          this.manualForm.reset({ title: '', raw_content: '' });
          this.isManualSubmitting = false;
        },
        error: (error: unknown) => {
          this.manualErrorMessage = this.getErrorMessage(error);
          this.isManualSubmitting = false;
        },
      });
  }

  protected submitUrlSource(): void {
    if (this.urlForm.invalid || this.isUrlSubmitting) {
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

    this.isUrlSubmitting = true;
    this.urlErrorMessage = null;
    this.createdUrlSource = null;

    this.sourcesApi
      .createUrlSource({
        title: title || null,
        url,
      })
      .subscribe({
        next: (source) => {
          this.createdUrlSource = source;
          this.urlForm.reset({ title: '', url: '' });
          this.isUrlSubmitting = false;
        },
        error: (error: unknown) => {
          this.urlErrorMessage = this.getErrorMessage(error);
          this.isUrlSubmitting = false;
        },
      });
  }

  protected hasManualControlError(
    controlName: 'title' | 'raw_content',
    errorCode: string,
  ): boolean {
    const control = this.manualForm.controls[controlName];
    return !!control.errors?.[errorCode] && (control.touched || control.dirty);
  }

  protected hasUrlControlError(controlName: 'title' | 'url', errorCode: string): boolean {
    const control = this.urlForm.controls[controlName];
    return !!control.errors?.[errorCode] && (control.touched || control.dirty);
  }

  private getErrorMessage(error: unknown): string {
    if (error instanceof HttpErrorResponse) {
      const detail = error.error?.detail;

      if (typeof detail === 'string' && detail.trim()) {
        return detail;
      }
    }

    return 'Could not create the source. Make sure the API is running.';
  }
}
