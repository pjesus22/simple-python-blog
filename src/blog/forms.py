from django import forms

from blog.models import Category


class PostForm(forms.Form):
    title = forms.CharField(max_length=255)
    summary = forms.CharField(max_length=255)
    content = forms.CharField()
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
