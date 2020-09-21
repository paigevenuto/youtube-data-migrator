$(function () {
  for (btn of $(".btn")) {
    mdc.ripple.MDCRipple.attachTo(btn);
  }

  for (field of $(".mdc-text-field")) {
    mdc.textField.MDCTextField.attachTo(field);
  }

  for (box of $(".mdc-checkbox")) {
    mdc.checkbox.MDCCheckbox.attachTo(box);
  }

  for (form of $(".mdc-form-field")) {
    mdc.formField.MDCFormField.attachTo(form);
  }
});
