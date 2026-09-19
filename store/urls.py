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
    path('dashboard/', views.custom_dashboard, name='dashboard'),
    path('dashboard/products/add/', views.dashboard_add_product, name='dashboard_add_product'),
    path('dashboard/brands/add/', views.dashboard_add_brand, name='dashboard_add_brand'),
    path('dashboard/categories/add/', views.dashboard_add_category, name='dashboard_add_category'),
    path('dashboard/products/<slug:slug>/edit/', views.dashboard_edit_product, name='dashboard_edit_product'),
    path('dashboard/products/<slug:slug>/delete/', views.dashboard_delete_product, name='dashboard_delete_product'),
    path('dashboard/products/', views.dashboard_products, name='dashboard_products'),
    path('dashboard/orders/', views.dashboard_orders, name='dashboard_orders'),
    path('dashboard/orders/<int:order_id>/', views.dashboard_order_detail, name='dashboard_order_detail'),
]

