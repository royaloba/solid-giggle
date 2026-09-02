# cart/cart.py
from decimal import Decimal
from django.conf import settings
from store.models import ProductVariant

CART_SESSION_ID = 'cart'

class Cart:
    def __init__(self, request):
        """Initialize the cart from the Django session."""
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, variant: ProductVariant, quantity: int = 1, override_quantity: bool = False):
        """Add a sneaker variant to the cart or update its quantity."""
        variant_id = str(variant.id)
        
        if variant_id not in self.cart:
            self.cart[variant_id] = {
                'quantity': 0,
                'price': str(variant.get_price())
            }

        if override_quantity:
            self.cart[variant_id]['quantity'] = quantity
        else:
            self.cart[variant_id]['quantity'] += quantity

        # Stock check guard
        if self.cart[variant_id]['quantity'] > variant.stock:
            self.cart[variant_id]['quantity'] = variant.stock

        self.save()

    def remove(self, variant: ProductVariant):
        """Remove a variant from the cart."""
        variant_id = str(variant.id)
        if variant_id in self.cart:
            del self.cart[variant_id]
            self.save()

    def clear(self):
        """Empty the cart session."""
        del self.session[CART_SESSION_ID]
        self.save()

    def save(self):
        """Mark the session as modified to ensure it gets saved."""
        self.session.modified = True

    def __iter__(self):
        """
        Iterate over the items in the cart and fetch related variants/products 
        from the database in one batch.
        """
        variant_ids = self.cart.keys()
        variants = ProductVariant.objects.filter(id__in=variant_ids).select_related('product').prefetch_related('product__images')
        
        cart_copy = {k: v.copy() for k, v in self.cart.items()}

        for variant in variants:
            item = cart_copy[str(variant.id)]
            item['variant'] = variant
            item['product'] = variant.product
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            # Get primary image or fallback to first
            images = list(variant.product.images.all())
            item['image'] = next((img for img in images if img.is_primary), images[0] if images else None)
            yield item

    def __len__(self) -> int:
        """Return total quantity of all items in the cart."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self) -> Decimal:
        """Calculate total price of all items in cart."""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())