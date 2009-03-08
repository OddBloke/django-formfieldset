#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from django import forms as django_forms
import forms


class FieldsetRenderTestCase(TestCase):
    def _test_form(self):
        class TestForm(django_forms.Form, forms.FieldsetMixin):
            test_field1 = django_forms.CharField()
            test_field2 = django_forms.CharField()
            test_field3 = django_forms.CharField()

            fieldsets = (
                (u'Fieldset1', {
                    'description': u'Test Description',
                    'fields': ('test_field1',),
                }),
                (u'Fieldset2', {
                    'fields': ('test_field2', 'test_field3'),
                }),
            )

            def clean_test_field2(self):
                raise django_forms.ValidationError(
                                [u'Test Error - Field Level - 1',
                                 u'Test Error - Field Level - 2'])

            def clean(self):
                raise django_forms.ValidationError(u'Test Error - Top Level')
        return TestForm

    def testFieldsetRender(self):
        RESPONSE = u"""<toplevelerrors><ul class="errorlist"><li>Test Error - Top Level</li></ul></toplevelerrors>
<fieldset>
<name>Fieldset1</name><help>Test Description</help>
<row><ul class="errorlist"><li>This field is required.</li></ul><input type="text" name="test_field1" id="id_test_field1" /></row>
</fieldset>
<fieldset>
<name>Fieldset2</name>
<row><ul class="errorlist"><li>Test Error - Field Level - 1</li><li>Test Error - Field Level - 2</li></ul><input type="text" name="test_field2" value="Test Value" id="id_test_field2" /></row>
<row><ul class="errorlist"><li>This field is required.</li></ul><input type="text" name="test_field3" id="id_test_field3" /></row>
</fieldset>"""
        form = self._test_form()(data={'test_field2': u'Test Value'})
        self.assertEqual(form.is_valid(), False)
        self.assertEqual(
            form._html_fieldset_output(
                '<fieldset>\n<name>%(name)s</name>' \
                    '%(description)s\n%(fields)s\n</fieldset>',
                '<row>%(errors)s%(field)s%(help_text)s</row>',
                '<toplevelerrors>%s</toplevelerrors>',
                '',
                '<help>%s</help>',
                False),
            RESPONSE
        )
