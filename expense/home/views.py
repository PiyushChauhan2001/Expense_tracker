from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Expense

@login_required
def home(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    # Ensure profile calculations are accurate
    profile.recalculate_totals()
    expenses = Expense.objects.filter(user=request.user)

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        amount_raw = request.POST.get('amount', '').strip()
        expense_type = request.POST.get('expense_type', 'Positive').strip()

        # Input Validation
        if not text:
            messages.error(request, 'Transaction description cannot be empty.')
            return redirect('home')

        try:
            amount = float(amount_raw)
            if amount <= 0:
                messages.error(request, 'Transaction amount must be greater than zero.')
                return redirect('home')
        except (ValueError, TypeError):
            messages.error(request, 'Please enter a valid numeric amount.')
            return redirect('home')

        if expense_type not in ('Positive', 'Negative'):
            messages.error(request, 'Invalid transaction type.')
            return redirect('home')

        # Create Expense Record
        Expense.objects.create(
            name=text,
            amount=amount,
            expense_type=expense_type,
            user=request.user
        )

        # Recalculate profile totals accurately
        profile.recalculate_totals()
        messages.success(request, f'Successfully added {expense_type.lower()} transaction: "{text}".')
        return redirect('home')

    context = {
        'profile': profile,
        'expenses': expenses,
    }
    return render(request, 'home.html', context)


@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense_name = expense.name
    expense.delete()
    
    # Recalculate user profile totals
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.recalculate_totals()
    
    messages.success(request, f'Deleted transaction "{expense_name}".')
    return redirect('home')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Expense Tracker, {user.username}!')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')