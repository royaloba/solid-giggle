from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # FIXED: Replaced 'drawer' with a standard 'profile' page route
    path('profile/', views.account_profile_view, name='profile'),
    
    path('download-orders/', views.download_orders_csv, name='download_orders'),
]