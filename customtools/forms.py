import json

from django import forms


class GenericSearchForm(forms.Form):
    """
    Formulaire de recherche
    """
    query = forms.CharField(label="", required=False, widget=forms.TextInput(attrs={"placeholder": "Recherche..."}))

class Select2Mixin:
    def __init__(self, *, url, placeholder, extraparams=None, **kwargs):
        self.url = url
        self.placeholder = placeholder
        self.extraparams = extraparams or {}
        self.minimum_input_length = kwargs.pop('minimum_input_length', 0)
        super().__init__(**kwargs)

    def widget_attrs(self, widget):
        return {
            "autoselect2": "true",
            "data-ajax--url": self.url,
            "data-minimum-input-length": self.minimum_input_length,
            "data-placeholder": self.placeholder,
            "data-extraparams": json.dumps(self.extraparams),
            "data-allow-clear": "true"
        }

class SelectedOnlyMultipleSelect(forms.widgets.SelectMultiple):
    """
    Create options only for already selected elemetns. Rest of options will be populated through select2 API.
    """

    def optgroups(self, name, value, attrs=None):
        """Return a list of optgroups for this widget."""
        groups = []
        for index, choice in enumerate(self.choices.queryset.filter(id__in=value)):
            subgroup = []
            group_name = None
            groups.append((group_name, subgroup, index))
            subgroup.append(self.create_option(
                name, choice.id, str(choice), selected=True, index=index, attrs=attrs,
            ))
        return groups


class Select2MutipleField(Select2Mixin, forms.ModelMultipleChoiceField):
    """
    Form field compatible with select2 javascipt library.
    The provided url should follow this documentation : https://select2.org/data-sources/ajax
    """
    widget = SelectedOnlyMultipleSelect