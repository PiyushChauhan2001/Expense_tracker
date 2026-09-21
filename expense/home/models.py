from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone

TYPE = (
    ('Positive', 'Positive'),
    ('Negative', 'Negative')
)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True, blank=True)
    income = models.FloatField(default=0.0)
    expenses = models.FloatField(default=0.0)
    balance = models.FloatField(default=0.0)

    def recalculate_totals(self):
        """Recalculates profile total income, expenses, and net balance based on stored Expense records."""
        if not self.user:
            return self

        user_expenses = Expense.objects.filter(user=self.user)
        
        pos_total = user_expenses.filter(expense_type='Positive').aggregate(Sum('amount'))['amount__sum'] or 0.0
        neg_total = user_expenses.filter(expense_type='Negative').aggregate(Sum('amount'))['amount__sum'] or 0.0

        self.income = float(pos_total)
        self.expenses = float(neg_total)
        self.balance = self.income - self.expenses
        self.save()
        return self

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{username}'s Profile (Balance: {self.balance})"


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_expenses', null=True, blank=True)
    name = models.CharField(max_length=100)
    amount = models.FloatField(default=0.0)
    expense_type = models.CharField(max_length=100, choices=TYPE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f"{self.name} - ${self.amount} ({self.expense_type})"