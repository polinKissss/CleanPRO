import re

from django import forms
from .models import CallbackRequest


class CallbackForm(forms.ModelForm):
    class Meta:
        model = CallbackRequest
        fields = ['name', 'phone', 'email', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if len(name) < 2:
            raise forms.ValidationError('Укажите имя (минимум 2 символа).')
        return name

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if not re.fullmatch(r'^\+?[\d\s()-]{10,20}$', phone):
            raise forms.ValidationError(
                'Телефон в формате +7 (999) 123-45-67 или 10–20 цифр.')
        return phone

    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        if len(message) < 10:
            raise forms.ValidationError('Опишите задачу подробнее (минимум 10 символов).')
        return message

