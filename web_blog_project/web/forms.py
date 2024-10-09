from django import forms
from .models import Item, Comment
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price', 'start_date', 'end_date', 'image']
        widgets = {
             'start_date': DateTimePickerInput(format='%Y-%m-%d %H:%M:%S'),
            'end_date': DateTimePickerInput(format='%Y-%m-%d %H:%M:%S'),
        }

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].input_formats = ['%Y-%m-%d %H:%M:%S']
        self.fields['end_date'].input_formats = ['%Y-%m-%d %H:%M:%S']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
