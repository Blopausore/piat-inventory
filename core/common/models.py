from django.db import models
from django.core.exceptions import ValidationError

class Client(models.Model):
    name = models.CharField(max_length=255)

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    
class Currency(models.TextChoices):
    USD = 'USD', 'USD' 
    THB = 'THB', 'BHT'
    # EUR = 'EUR', 'Euro'
    # GBP = 'GBP', 'British Pound'
    # JPY = 'JPY', 'Japanese Yen'
