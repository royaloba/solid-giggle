from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('receipt/<str:reference>/', views.receipt_view, name='receipt'),
]