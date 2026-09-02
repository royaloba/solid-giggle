# payments/services.py
import requests
from django.conf import settings
from typing import Dict, Any

class PaystackService:
    BASE_URL = "https://api.paystack.co"

    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    def initialize_transaction(self, email: str, amount_kobo: int, reference: str, callback_url: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/transaction/initialize"
        payload = {
            "email": email,
            "amount": amount_kobo,
            "reference": reference,
            "callback_url": callback_url,
        }
        response = requests.post(url, json=payload, headers=self.headers, timeout=15)
        response.raise_for_status()
        return response.json()

    def verify_transaction(self, reference: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/transaction/verify/{reference}"
        response = requests.get(url, headers=self.headers, timeout=15)
        response.raise_for_status()
        return response.json()