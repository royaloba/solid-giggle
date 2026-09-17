from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
import csv
from orders.models import Order 
from cart.cart import Cart 


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Auto-login after registration
            messages.success(request, "Registration successful! Welcome to Stylinsole.")
            return redirect('store:home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            # If they were trying to checkout before logging in, send them back there
            next_url = request.GET.get('next', 'store:home')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
        
    # Apply Tailwind classes to login form dynamically
    for field in form.fields.values():
        field.widget.attrs['class'] = 'w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-black outline-none transition'

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out securely.")
    return redirect('store:home')


@login_required
def account_drawer_view(request):
    """Safely gathers user statistics and renders the slide-out drawer."""
    # 1. Safely fetch the last 10 orders for this user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # 2. Fetch wishlist count using your exact related_name from store/models.py
    wishlist_count = request.user.wishlist_items.count()

    # 3. Fetch current cart count
    cart = Cart(request)

    return render(request, 'accounts/partials/account_drawer_content.html', {
        'orders': orders,
        'cart_count': len(cart),
        'wishlist_count': wishlist_count,
    })

@login_required
def download_orders_csv(request):
    """Generates a downloadable CSV file of the user's current orders."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="my_stylinsole_orders.csv"'},
    )
    
    writer = csv.writer(response)
    writer.writerow(["Order ID", "Date", "Items Count", "Total Amount (NGN)"])
    
    for order in orders:
        # Assumes your Order model has these fields; adjust as necessary
        item_count = sum(item.quantity for item in order.items.all()) if hasattr(order, 'items') else 0
        writer.writerow([
            f"#{order.id}", 
            order.created_at.strftime("%Y-%m-%d %H:%M"), 
            item_count, 
            order.total_amount
        ])
        
    return response