from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F, DecimalField, Value
from django.db.models.functions import Coalesce
from django.contrib import messages
from django.utils import timezone

from .models import LoanProfile, LoanPayment
from .forms import LoanProfileForm, LoanPaymentForm, LoanSearchForm, LoanUpdateForm


def overview(request):
    # Calculate totals using database aggregation
    total_loans = LoanProfile.objects.all()
    total_loan_amount = total_loans.aggregate(total=Sum('total_amount'))['total'] or 0

    # Calculate total paid amount by summing all payments
    total_paid_amount = LoanPayment.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_remaining_amount = total_loan_amount - total_paid_amount

    context = {
        'total_loan_amount': total_loan_amount,
        'total_paid_amount': total_paid_amount,
        'total_remaining_amount': total_remaining_amount,
        'loan_count': total_loans.count(),
    }
    return render(request, 'overview.html', context)


def create_loan(request):
    search_form = LoanSearchForm(request.GET or None)
    loan_form = LoanProfileForm(request.POST or None)

    # Filter loans for search
    loans = LoanProfile.objects.all()
    if search_form.is_valid() and search_form.cleaned_data.get('search'):
        search_term = search_form.cleaned_data['search']
        loans = loans.filter(name__icontains=search_term)

    if request.method == 'POST' and loan_form.is_valid():
        loan_form.save()
        messages.success(request, 'Loan profile created successfully!')
        return redirect('create_loan')

    context = {
        'loan_form': loan_form,
        'search_form': search_form,
        'loans': loans,
    }
    return render(request, 'create_loan.html', context)


def make_payment(request):
    if request.method == 'POST':
        form = LoanPaymentForm(request.POST)
        if form.is_valid():
            loan_profile = form.cleaned_data['loan_profile']
            amount = form.cleaned_data['amount']

            # Check if payment exceeds remaining amount
            if amount > loan_profile.remaining_amount:
                messages.error(request,
                               f"Payment amount (${amount}) exceeds remaining balance (${loan_profile.remaining_amount})")
            else:
                form.save()
                messages.success(request, 'Payment recorded successfully!')
                return redirect('make_payment')
    else:
        form = LoanPaymentForm()

    # Get loans with their payment sums using annotation
    loans = LoanProfile.objects.annotate(
        paid_sum=Coalesce(Sum('payments__amount'), Value(0), output_field=DecimalField())
    ).annotate(
        remaining=F('total_amount') - F('paid_sum')
    ).filter(remaining__gt=0)

    total_loans = LoanProfile.objects.all()
    total_loan_amount = total_loans.aggregate(total=Sum('total_amount'))['total'] or 0

    # Calculate total paid amount by summing all payments
    total_paid_amount = LoanPayment.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_remaining_amount = total_loan_amount - total_paid_amount


    today = timezone.now().date()
    total_payments_today = LoanPayment.objects.filter(
        payment_date__date=today
    ).count()

    context = {
        'form': form,
        'loans': loans,
        'total_active_balance': total_remaining_amount,
        'today_payments': total_payments_today,
    }
    return render(request, 'payment.html', context)


def loan_history(request):
    search_form = LoanSearchForm(request.GET or None)

    # Get loans with annotations for paid amount and remaining
    loans = LoanProfile.objects.annotate(
        paid_sum=Coalesce(Sum('payments__amount'), Value(0), output_field=DecimalField())
    ).annotate(
        remaining=F('total_amount') - F('paid_sum')
    ).prefetch_related('payments')

    if search_form.is_valid() and search_form.cleaned_data.get('search'):
        search_term = search_form.cleaned_data['search']
        loans = loans.filter(name__icontains=search_term)

    # Prepare data for template
    loan_data = []
    for loan in loans:
        loan_data.append({
            'profile': loan,
            'total_amount': loan.total_amount,
            'paid_amount': loan.paid_sum,
            'remaining_amount': loan.remaining,
            'entry_date': loan.loan_entry_date,
            'payments': loan.payments.all().order_by('-payment_date'),
            'payment_count': loan.payments.count(),
        })

    context = {
        'loan_data': loan_data,
        'search_form': search_form,
        'total_profiles': loans.count(),
        'total_transactions': LoanPayment.objects.all().count(),
    }
    return render(request, 'history.html', context)


def delete_loan(request):
    search_form = LoanSearchForm(request.GET or None)

    loans = LoanProfile.objects.all()
    if search_form.is_valid() and search_form.cleaned_data.get('search'):
        search_term = search_form.cleaned_data['search']
        loans = loans.filter(name__icontains=search_term)

    if request.method == 'POST':
        loan_id = request.POST.get('loan_id')
        if loan_id:
            loan = get_object_or_404(LoanProfile, id=loan_id)
            loan.delete()
            messages.success(request, 'Loan profile deleted successfully!')
            return redirect('delete_loan')

    context = {
        'search_form': search_form,
        'loans': loans,
    }
    return render(request, 'delete_loan.html', context)


def update_loan(request):
    search_form = LoanSearchForm(request.GET or None)

    # Get loans with annotations
    loans = LoanProfile.objects.annotate(
        paid_sum=Coalesce(Sum('payments__amount'), Value(0), output_field=DecimalField())
    ).annotate(
        remaining=F('total_amount') - F('paid_sum')
    )

    if search_form.is_valid() and search_form.cleaned_data.get('search'):
        search_term = search_form.cleaned_data['search']
        loans = loans.filter(name__icontains=search_term)

    # Handle loan selection
    selected_loan = None
    form = None

    if request.method == 'GET' and 'loan_id' in request.GET:
        loan_id = request.GET.get('loan_id')
        selected_loan = get_object_or_404(LoanProfile, id=loan_id)
        form = LoanUpdateForm(instance=selected_loan)

    if request.method == 'POST':
        loan_id = request.POST.get('loan_id')
        selected_loan = get_object_or_404(LoanProfile, id=loan_id)
        form = LoanUpdateForm(request.POST, instance=selected_loan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loan profile updated successfully!')
            return redirect('update_loan')

    context = {
        'search_form': search_form,
        'loans': loans,
        'selected_loan': selected_loan,
        'form': form,
    }
    return render(request, 'update_loan.html', context)