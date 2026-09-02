# payments/urls.py
from django.urls import path
from .views import initiate_payment_view, payment_callback_view, paystack_webhook_view

app_name = 'payments'

urlpatterns = [
    path('initiate/<int:order_id>/', initiate_payment_view, name='initiate'),
    path('callback/', payment_callback_view, name='callback'),
    path('webhook/', paystack_webhook_view, name='webhook'),
]