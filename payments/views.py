# payments/views.py
import hmac
import hashlib
import json
import logging
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from orders.models import Order
from .services import PaystackService

logger = logging.getLogger(__name__)


def initiate_payment_view(request: HttpRequest, order_id: int):
    """Initializes checkout with Paystack and redirects customer."""
    order = get_object_or_404(Order, id=order_id, status=Order.PaymentStatus.PENDING)
    paystack = PaystackService()

    try:
        response = paystack.initialize_transaction(
            email=order.email,
            amount_kobo=order.amount_in_kobo,
            reference=order.reference,
            callback_url=settings.PAYSTACK_CALLBACK_URL
        )

        if response.get("status") is True:
            authorization_url = response["data"]["authorization_url"]
            return redirect(authorization_url)
        else:
            logger.error(f"Paystack Init Failed for Order {order.reference}: {response}")
            return render(request, "payments/failed.html", {"message": "Could not initialize payment."})

    except Exception as e:
        logger.exception(f"Error initializing Paystack transaction: {e}")
        return render(request, "payments/failed.html", {"message": "Payment gateway error. Please try again."})


@require_GET
def payment_callback_view(request: HttpRequest):
    """Handles the user browser redirect after Paystack checkout."""
    reference = request.GET.get("reference")
    if not reference:
        return redirect("store:home")

    order = get_object_or_404(Order, reference=reference)

    # Note: Rely primarily on the webhook for database mutation;
    # verify here for immediate UI responsiveness.
    paystack = PaystackService()
    try:
        result = paystack.verify_transaction(reference)
        data = result.get("data", {})

        if data.get("status") == "success":
            return render(request, "payments/success.html", {"order": order})
        else:
            return render(request, "payments/failed.html", {"order": order})
    except Exception as e:
        logger.error(f"Callback verification check failed: {e}")
        return render(request, "payments/pending.html", {"order": order})


@csrf_exempt
@require_POST
def paystack_webhook_view(request: HttpRequest):
    """
    Listens for Paystack webhooks, validates signature using HMAC-SHA512,
    and idempotently updates order status and fulfills purchases.
    """
    paystack_signature = request.headers.get("x-paystack-signature") or request.META.get("HTTP_X_PAYSTACK_SIGNATURE")
    
    if not paystack_signature:
        logger.warning("Paystack webhook received without signature header.")
        return HttpResponse(status=400)

    # 1. Verify HMAC SHA512 Signature
    secret_bytes = settings.PAYSTACK_SECRET_KEY.encode("utf-8")
    computed_signature = hmac.new(
        key=secret_bytes,
        msg=request.body,
        digestmod=hashlib.sha512
    ).hexdigest()

    if not hmac.compare_digest(computed_signature, paystack_signature):
        logger.warning("Paystack webhook signature mismatch - possible spoofing attempt.")
        return HttpResponse(status=400)

    # 2. Parse Webhook Payload
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from Paystack webhook.")
        return HttpResponse(status=400)

    event = payload.get("event")
    data = payload.get("data", {})

    # 3. Process 'charge.success'
    if event == "charge.success":
        reference = data.get("reference")
        amount_paid_kobo = data.get("amount")
        tx_id = data.get("id")

        try:
            with transaction.atomic():
                # Lock row to prevent race condition between webhook & callback
                order = Order.objects.select_for_update().get(reference=reference)

                if order.status == Order.PaymentStatus.SUCCESS:
                    # Idempotency check: Already processed
                    return HttpResponse(status=200)

                # Validate amount received matches order amount exactly
                if amount_paid_kobo != order.amount_in_kobo:
                    logger.error(
                        f"Amount mismatch for {order.reference}. Expected {order.amount_in_kobo}, got {amount_paid_kobo}"
                    )
                    order.status = Order.PaymentStatus.FAILED
                    order.save(update_fields=["status", "updated_at"])
                    return HttpResponse(status=200)

                # Mark Order as Paid
                order.status = Order.PaymentStatus.SUCCESS
                order.paystack_transaction_id = str(tx_id)
                order.save(update_fields=["status", "paystack_transaction_id", "updated_at"])

                # Fulfill order (Reduce sneaker inventory, clear session cart, trigger confirmation email)
                _fulfill_order(order)

        except Order.DoesNotExist:
            logger.error(f"Order reference {reference} not found during webhook processing.")
            return HttpResponse(status=404)
        except Exception as e:
            logger.exception(f"Unexpected error while processing webhook for {reference}: {e}")
            return HttpResponse(status=500)

    return HttpResponse(status=200)


def _fulfill_order(order: Order):
    """Hook for inventory deduction, order confirmation emails, and alerts."""
    logger.info(f"Successfully fulfilled Order {order.reference} for {order.email}")
    # Example: Deduct ProductVariant.stock, send Celery tasks, etc.