# cart/urls.py
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('drawer/', views.cart_drawer, name='drawer'),
    path('badge/', views.cart_badge, name='badge'),
    path('add/<int:variant_id>/', views.cart_add, name='add'),
    path('update/<int:variant_id>/', views.cart_update, name='update'),
    path('remove/<int:variant_id>/', views.cart_remove, name='remove'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
]