from django import forms
from .models import Item, Comment
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price', 'start_date', 'end_date', 'image','status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': DateTimePickerInput(format='%Y-%m-%d %H:%M:%S'),
            'end_date': DateTimePickerInput(format='%Y-%m-%d %H:%M:%S'),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].input_formats = ['%Y-%m-%d %H:%M:%S']
        self.fields['end_date'].input_formats = ['%Y-%m-%d %H:%M:%S']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class ItemStatusForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
