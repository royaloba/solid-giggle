import uuid
from django.db import models
from django.conf import settings

class Order(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    reference = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Customer & Shipping Details (CRITICAL FIX)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    state = models.CharField(max_length=50)

    # Payment Details
    total_amount = models.DecimalField(max_digits=12, decimal_places=2) # in Naira
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    paystack_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.reference} - ₦{self.total_amount} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"ORD-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    @property
    def amount_in_kobo(self) -> int:
        return int(self.total_amount * 100)

    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00)
    
    @property
    def subtotal(self):
        # Calculates the item subtotal without needing a template tag
        return self.total_amount - self.shipping_fee

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey('store.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    product_name = models.CharField(max_length=255) 
    size = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=12, decimal_places=2) 
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product_name} (Size {self.size})"

    @property
    def total_price(self):
        safe_price = self.price or 0
        safe_quantity = self.quantity or 0
        return safe_price * safe_quantity