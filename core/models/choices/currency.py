from django.db import models

class Currency(models.TextChoices):
    USD = 'USD', 'US Dollar'
    THB = 'THB', 'Thai Baht'
    # EUR = 'EUR', 'Euro'
    # GBP = 'GBP', 'British Pound'
    # JPY = 'JPY', 'Japanese Yen'
