from django.contrib import admin
from .models import LoanProfile, LoanPayment

@admin.register(LoanProfile)
class LoanProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_amount', 'paid_amount', 'remaining_amount', 'loan_entry_date', 'is_fully_paid')
    list_filter = ('loan_entry_date',)
    search_fields = ('name',)

@admin.register(LoanPayment)
class LoanPaymentAdmin(admin.ModelAdmin):
    list_display = ('loan_profile', 'amount', 'payment_date')
    list_filter = ('payment_date',)
    search_fields = ('loan_profile__name', 'notes')