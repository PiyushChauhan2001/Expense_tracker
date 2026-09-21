from django.contrib import admin
from .models import Profile, Expense

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'income', 'expenses', 'balance')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('income', 'expenses', 'balance')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'amount', 'expense_type', 'created_at')
    list_filter = ('expense_type', 'created_at')
    search_fields = ('name', 'user__username')