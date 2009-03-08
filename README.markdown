**django-formfieldset** is a simple Django app that provides a mix-in class
for admin-like fieldset rendering.


Features
========

 * Fieldset functionality similar to `ModelAdmin`
 * Shorthand rendering functions with fieldsets
   * as `P`
   * as `TABLE`
   * as `UL`
 * Overrides nothing in `django.forms.Form`


Installation
============

 1. Add 'django-formfieldset' directory to your Python path.
 2. Add 'formfieldset' to your `INSTALLED_APPS` tuple
    found in your settings file. (optional - to be able to run tests)
 3. Create your forms with `FieldsetMixin`


Usage
=====

 * Add a `fieldsets` attribute to your form. See [admin docs][ref1] for
   detailed explanation.
 * Render your form with fieldset enabled methods:
   * You can use `iter_fieldsets()` for custom form rendering. It will yield
     `Fieldset` objects. `Fieldset`s act as iterators for widgets in them.
   * You can use `as_fieldset_table()`, `as_fieldset_ul()` and
     `as_fieldset_p()` methods that act like built-in `as_*` method except
     fieldset support.


  [ref1]: http://docs.djangoproject.com/en/dev/ref/contrib/admin/#fieldsets
