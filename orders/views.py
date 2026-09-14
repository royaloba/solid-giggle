from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.http import Http404
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import CheckoutForm

def checkout_view(request):
    cart = Cart(request)
    
    if len(cart) == 0:
        messages.error(request, "Your cart is empty. Add some sneakers before checking out.")
        return redirect('store:home')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    if request.user.is_authenticated:
                        order.user = request.user
                    
                    order.total_amount = cart.get_total_price()
                    order.save() # Shipping details are now saved securely!

                    for item in cart:
                        variant = item['variant']
                        
                        # NEW CHECK: Look at the boolean toggle instead of numeric stock
                        if not variant.product.is_in_stock:
                            raise ValueError(f"Sorry, {item['product'].name} is currently sold out.")

                        OrderItem.objects.create(
                            order=order,
                            variant=variant,
                            product_name=item['product'].name,
                            size=variant.size,
                            price=item['price'],
                            quantity=item['quantity']
                        )

                    cart.clear()
                return redirect('payments:initiate', order_id=order.id)

            except ValueError as e:
                messages.error(request, str(e))
                return redirect('cart:drawer') 
            except Exception as e:
                messages.error(request, "A system error occurred. Please try again.")
                
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            }
        form = CheckoutForm(initial=initial_data)

    return render(request, 'orders/checkout.html', {'form': form, 'cart': cart})

def receipt_view(request, reference):
    """Allows users or admins to view and print the order invoice."""
    order = get_object_or_404(Order, reference=reference)
    
    # Security: Ensure only the person who made the order (or an admin) can see the receipt
    if order.user and request.user != order.user and not request.user.is_staff:
        raise Http404("Receipt not found.")
        
    return render(request, 'orders/receipt.html', {'order': order})