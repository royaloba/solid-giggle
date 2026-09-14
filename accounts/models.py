from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Added specifically for Nigerian e-commerce logistics
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.email or self.username