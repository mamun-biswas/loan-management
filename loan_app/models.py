from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class LoanProfile(models.Model):
    name = models.CharField(max_length=200)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    loan_entry_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - BDT-{self.total_amount}"

    @property
    def paid_amount(self):
        return sum(payment.amount for payment in self.payments.all())

    @property
    def remaining_amount(self):
        return self.total_amount - self.paid_amount

    @property
    def is_fully_paid(self):
        return self.remaining_amount <= 0


class LoanPayment(models.Model):
    loan_profile = models.ForeignKey(LoanProfile, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Payment of ${self.amount} for {self.loan_profile.name}"

    def save(self, *args, **kwargs):
        # Check if payment exceeds remaining amount
        if self.amount > self.loan_profile.remaining_amount:
            raise ValueError("Payment amount cannot exceed remaining loan amount")
        super().save(*args, **kwargs)