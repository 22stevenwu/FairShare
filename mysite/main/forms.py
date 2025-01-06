from django import forms
from .models import Bill

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill  
        fields = ['name', 'total_amount', 'tip_percentage']  
        labels = {
            'name': 'Bill Name',
            'total_amount': 'Total Amount',
            'tips_percentage': 'Tip (%)',
        }

    def clean_total_amount(self):
        total_amount = self.cleaned_data.get('total_amount')
        if total_amount <= 0:
            raise forms.ValidationError("Total amount must be greater than zero.")
        return total_amount
