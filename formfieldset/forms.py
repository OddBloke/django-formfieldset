from django import forms as django_forms
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode


class Fieldset(object):
    "Simple iterable for holding fieldset information."

    def __init__(self, form, name=None, fields=(),
                 description=None, extra_content={}):
        self.form = form
        self.name = name
        self.fields = fields
        self.description = description
        self.extra_content = extra_content

    def __iter__(self):
        "Iterates through fields in the fieldset."
        for field in self.fields:
            yield django_forms.forms.BoundField(self.form,
                                                self.form.fields[field],
                                                field)

    def html_output(self, normal_row, error_row, help_text_html,
                    errors_on_separate_row,
                    error_class=django_forms.util.ErrorList, label_suffix=':'):
        output = []
        for bf in self:
            # Escape and cache in local variable.
            bf_errors = error_class([escape(error) for error in bf.errors])
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend(
                        [u'(Hidden field %s) %s' % (bf.name, force_unicode(e))
                            for e in bf_errors])
                hidden_fields.append(unicode(bf))
            else:
                if errors_on_separate_row and bf_errors:
                    output.append(error_row % force_unicode(bf_errors))
                if bf.label:
                    label = escape(force_unicode(bf.label))
                    # Only add the suffix if the label does not end in
                    # punctuation.
                    if label_suffix:
                        if label[-1] not in ':?.!':
                            label += label_suffix
                    label = bf.label_tag(label) or ''
                else:
                    label = ''
                if bf.field.help_text:
                    help_text = help_text_html % force_unicode(
                                                    bf.field.help_text)
                else:
                    help_text = u''
                output.append(normal_row % {'errors': force_unicode(bf_errors),
                                            'label': force_unicode(label),
                                            'field': unicode(bf),
                                            'help_text': help_text})
        return output

    def as_table(self):
        fields = self.html_output(
            u'<tr><th>%(label)s</th>'
                u'<td>%(errors)s%(field)s%(help_text)s</td></tr>',
            u'<tr><td colspan="2">%s</td></tr>',
            u'<br />%s',
            False)
        description = ''
        if self.description is not None:
            description = self.description
        return mark_safe(
            u'<tr><th colspan="2">'
            u'<h2>%(name)s</h2>%(description)s</th></tr>%(fields)s'
                    % {'name': self.name,
                       'description': description,
                       'fields': u'\n'.join(fields),
                      })


class FieldsetMixin(object):
    def iter_fieldsets(self):
        "Iterates fieldsets."
        for name, options in self.fieldsets:
            yield Fieldset(self, name, **options)

    def _html_fieldset_output(self,
                              fieldset_row,
                              normal_row,
                              error_row,
                              row_ender,
                              help_text_html,
                              errors_on_separate_row):
        "Helper function for outputting fieldsets as HTML. " \
        "Used by as_fieldset_table(), as_fieldset_ul(), as_fieldset_p()."

        # Errors that should be displayed above all fields.
        top_errors = self.non_field_errors()
        output, hidden_fields = [], []
        for fieldset in self.iter_fieldsets():
            fieldset_output = fieldset.html_output(
                self,
                normal_row,
                error_row,
                help_text_html,
                errors_on_separate_row,
                error_class=self.error_class,
                label_suffix=self.label_suffix)
            if fieldset.description:
                description = help_text_html % force_unicode(
                                                         fieldset.description)
            else:
                description = u''
            output.append(fieldset_row % {
                                    'name': fieldset.name,
                                    'description': description,
                                    'fields': u'\n'.join(fieldset_output)})
        if top_errors:
            output.insert(0, error_row % force_unicode(top_errors))
        if hidden_fields: # Insert any hidden fields in the last row.
            str_hidden = u''.join(hidden_fields)
            if output:
                last_row = output[-1]
                # Chop off the trailing row_ender (e.g. '</td></tr>') and
                # insert the hidden fields.
                output[-1] = last_row[:-len(row_ender)] + str_hidden + \
                                                                     row_ender
            else:
                # If there aren't any rows in the output, just append the
                # hidden fields.
                output.append(str_hidden)
        return mark_safe(u'\n'.join(output))

    def as_fieldset_table(self):
        "Returns this form's fieldsets rendered as HTML <tr>s -- " \
        "excluding the <table></table>."
        return self._html_fieldset_output(
            u'<tr><th colspan="2"><h2>%(name)s</h2>%(description)s</th></tr>%(fields)s',
            u'<tr><th>%(label)s</th><td>%(errors)s%(field)s%(help_text)s' \
                                                                u'</td></tr>',
            u'<tr><td colspan="2">%s</td></tr>',
            '</td></tr>',
            u'<br />%s',
            False)

    def as_fieldset_ul(self):
        "Returns this form's fieldsets rendered as HTML <li>s -- " \
        "excluding the <ul></ul>."
        return self._html_fieldset_output(
            u'<li>\n<h2>%(name)s</h2>%(description)s\n<ul>\n%(fields)s\n'\
                                                              u'</ul>\n</li>',
            u'<li>%(errors)s%(label)s %(field)s%(help_text)s</li>',
            u'<li>%s</li>',
            '</li></ul></li>',
            u' %s',
            False)

    def as_fieldset_p(self):
        "Returns this form's fieldsets rendered as HTML <p>s."
        return self._html_fieldset_output(
            u'<div>\n<h2>%(name)s</h2>%(description)s\n%(fields)s\n</div>',
            u'<p>%(label)s %(field)s%(help_text)s</p>',
            u'%s',
            u'</p></div>',
            u' %s',
            True)
