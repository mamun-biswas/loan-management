from django import forms
from .models import LoanProfile, LoanPayment
from django.core.validators import MinValueValidator

class LoanProfileForm(forms.ModelForm):
    class Meta:
        model = LoanProfile
        fields = ['name', 'total_amount', 'loan_entry_date']
        widgets = {
            'loan_entry_date': forms.DateInput(attrs={'type': 'date'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter borrower name'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter loan amount', 'step': '0.01'}),
        }

class LoanPaymentForm(forms.ModelForm):
    class Meta:
        model = LoanPayment
        fields = ['loan_profile', 'amount', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter payment amount', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional notes'}),
        }

class LoanSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name...'
        })
    )

class LoanUpdateForm(forms.ModelForm):
    class Meta:
        model = LoanProfile
        fields = ['name', 'total_amount', 'loan_entry_date']
        widgets = {
            'loan_entry_date': forms.DateInput(attrs={'type': 'date'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }