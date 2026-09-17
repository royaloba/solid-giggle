from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('drawer/', views.account_drawer_view, name='drawer'),
    path('download-orders/', views.download_orders_csv, name='download_orders'),
]