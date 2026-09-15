from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Assuming you have a home/index route here
    path('', views.home_view, name='home'), # The new homepage route
    path('store/', views.product_list, name='list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
]

