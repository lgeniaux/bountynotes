import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';

type UrlFormGroup = FormGroup<{
  title: FormControl<string | null>;
  url: FormControl<string | null>;
}>;

@Component({
  selector: 'app-add-url-form',
  imports: [ReactiveFormsModule],
  templateUrl: './add-url-form.component.html',
  styleUrl: './add-url-form.component.css',
})
export class AddUrlFormComponent {
  @Input({ required: true }) form!: UrlFormGroup;
  @Input({ required: true }) isSubmitting = false;
  @Input({ required: true }) submitLabel = 'Add source';

  @Output() submitted = new EventEmitter<void>();

  protected hasControlError(controlName: 'title' | 'url', errorCode: string): boolean {
    const control = this.form.controls[controlName];
    return !!control.errors?.[errorCode] && (control.touched || control.dirty);
  }
}
