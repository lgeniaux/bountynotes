import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';

type ManualFormGroup = FormGroup<{
  title: FormControl<string | null>;
  raw_content: FormControl<string | null>;
}>;

@Component({
  selector: 'app-add-manual-form',
  imports: [ReactiveFormsModule],
  templateUrl: './add-manual-form.component.html',
  styleUrl: './add-manual-form.component.css',
})
export class AddManualFormComponent {
  @Input({ required: true }) form!: ManualFormGroup;
  @Input({ required: true }) isSubmitting = false;
  @Input({ required: true }) submitLabel = 'Add source';

  @Output() submitted = new EventEmitter<void>();

  protected hasControlError(controlName: 'title' | 'raw_content', errorCode: string): boolean {
    const control = this.form.controls[controlName];
    return !!control.errors?.[errorCode] && (control.touched || control.dirty);
  }
}
