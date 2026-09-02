from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Assuming you have a home/index route here
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
]

