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

  function collapse(event) {
    $(event.target).parent().next().toggleClass("hidden-item");
    if ($(event.target).text() == "expand_less") {
      $(event.target).text("expand_more");
    } else {
      $(event.target).text("expand_less");
    }
  }

  for (let list of $(".mdc-list-group").children()) {
    if ($(list).children().length == 0) {
      $(list).parent().prev().addClass("hidden-item");
    }
  }

  $(".collapse-btn").on("click", collapse);
});
