from django import forms
from .models import Bill, User

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill  
        fields = ['name', 'total_amount', 'tip_percentage', 'tax_amount']  
        labels = {
            'name': 'Bill Name',
            'total_amount': 'Total Amount ($)',
            'tip_percentage': 'Tip (%)',
            'tax_amount': 'Tax ($)',
        }

    def clean_total_amount(self):
        total_amount = self.cleaned_data.get('total_amount')
        if total_amount <= 0:
            raise forms.ValidationError("Total amount must be greater than zero.")
        return total_amount

class BillSplitForm(forms.Form):
    name = forms.CharField(max_length=255, label="Participant's Name")  
    amount_spent = forms.DecimalField(max_digits=10, decimal_places=2, label="Amount Spent") 