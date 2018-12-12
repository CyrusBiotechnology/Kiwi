from django import forms
# from jsonfield.fields import JSONFormField
import json


class IssueTypeForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.issue_types = kwargs.pop('issue_types')
        self.project = json.dumps(kwargs.pop('project'))
        super().__init__(*args, **kwargs)

        choices = tuple((issue_type, issue_type['name']) for issue_type in self.issue_types)
        self.fields['issue_types'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=choices)
        self.fields['project'] = forms.CharField(widget=forms.HiddenInput(), initial=self.project)
