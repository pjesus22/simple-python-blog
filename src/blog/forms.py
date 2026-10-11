from django import forms

from blog.models import Category, Post


class PostForm(forms.Form):
    title = forms.CharField(max_length=255)
    summary = forms.CharField(max_length=255)
    content = forms.CharField()
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance

    def clean_title(self):
        title = self.cleaned_data["title"]
        dupes = Post.objects.filter(title=title)
        if self.instance is not None:
            dupes = dupes.exclude(pk=self.instance.pk)
        if dupes.exists():
            raise forms.ValidationError("A post with this title already exists.")
        return title
