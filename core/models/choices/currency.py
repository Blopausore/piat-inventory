from django.db import models

class Currency(models.TextChoices):
    USD = 'USD', 'USD' 
    THB = 'THB', 'BHT'
    # EUR = 'EUR', 'Euro'
    # GBP = 'GBP', 'British Pound'
    # JPY = 'JPY', 'Japanese Yen'
