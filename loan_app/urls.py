from django.urls import path
from . import views

urlpatterns = [
    path('', views.overview, name='overview'),
    path('overview/', views.overview, name='overview'),
    path('create-loan/', views.create_loan, name='create_loan'),
    path('make-payment/', views.make_payment, name='make_payment'),
    path('loan-history/', views.loan_history, name='loan_history'),
    path('delete-loan/', views.delete_loan, name='delete_loan'),
    path('update-loan/', views.update_loan, name='update_loan'),
]