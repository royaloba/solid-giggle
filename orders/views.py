

# Create your views here.
# orders/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import CheckoutForm

def checkout_view(request):
    cart = Cart(request)
    
    # Block checkout if cart is empty
    if len(cart) == 0:
        messages.error(request, "Your cart is empty. Add some sneakers before checking out.")
        return redirect('store:home')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        
        if form.is_valid():
            try:
                # Wrap in atomic block: Either everything saves, or nothing saves.
                with transaction.atomic():
                    
                    # 1. Create the Order
                    order = form.save(commit=False)
                    if request.user.is_authenticated:
                        order.user = request.user
                    
                    order.total_amount = cart.get_total_price()
                    
                    # Save shipping data to a JSON field or separate model if you expand later
                    # For now, we'll store basic order state
                    order.save()

                    # 2. Move cart items into OrderItems in the database
                    for item in cart:
                        variant = item['variant']
                        
                        # (Optional) Basic stock check before selling
                        if variant.stock < item['quantity']:
                            raise ValueError(f"Sorry, {item['product'].name} in size {variant.size} only has {variant.stock} left.")

                        OrderItem.objects.create(
                            order=order,
                            variant=variant,
                            product_name=item['product'].name,
                            size=variant.size,
                            price=item['price'],
                            quantity=item['quantity']
                        )

                    # 3. Clear the session cart because the order is now recorded
                    cart.clear()

                # 4. Handoff to Paystack Initialization View
                # We redirect to the 'payments:initiate' route we built previously
                return redirect('payments:initiate', order_id=order.id)

            except ValueError as e:
                # Catch the stock error we raised above
                messages.error(request, str(e))
                return redirect('cart:drawer') # Or wherever your full cart page is
            except Exception as e:
                messages.error(request, "A system error occurred. Please try again.")
                # Log the exception here
                
    else:
        # Pre-fill form if user is logged in
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            }
        form = CheckoutForm(initial=initial_data)

    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart': cart
    })