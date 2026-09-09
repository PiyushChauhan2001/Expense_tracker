from django.db import models
from django.contrib.auth.models import User

# Create your models here.

TYPE = (
    ('Positive', 'Positive'),
    ('Negative', 'Negative')
)

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    income = models.FloatField()
    expenses = models.FloatField(default=0)
    balance = models.FloatField(blank=True, null=True)



class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    amount = models.FloatField(null=True)
    expense_type = models.CharField(max_length=100, choices=TYPE)

    def __str__(self):
        return self.name