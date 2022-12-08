from django import forms

from .models import Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group')
        labels = {
            'text': ('Текст поста'),
            'group': ('Группа'),
        }
        help_texts = {
            'text':('Текст поста не может быть пустым')
        }

    def clean_text(self):
        data = self.cleaned_data['text']
        if not data:
            raise forms.ValidationError(
                'Вы обязательно должны что-нибудь написать!'
            )
        return data
