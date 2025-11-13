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

  protected isSubmitting = false;
  protected errorMessage: string | null = null;
  protected createdSource: SourceRead | null = null;

  protected submitManualSource(): void {
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

    this.isSubmitting = true;
    this.errorMessage = null;
    this.createdSource = null;

    this.sourcesApi
      .createManualSource({
        title: title || null,
        raw_content: rawContent,
      })
      .subscribe({
        next: (source) => {
          this.createdSource = source;
          this.manualForm.reset({ title: '', raw_content: '' });
          this.isSubmitting = false;
        },
        error: (error: unknown) => {
          this.errorMessage = this.getErrorMessage(error);
          this.isSubmitting = false;
        },
      });
  }

  protected hasControlError(controlName: 'title' | 'raw_content', errorCode: string): boolean {
    const control = this.manualForm.controls[controlName];
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
