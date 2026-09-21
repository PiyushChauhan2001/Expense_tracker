from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Profile, Expense

class ExpenseTrackerTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'StrongPass123!'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.home_url = reverse('home')
        self.login_url = reverse('login')
        self.signup_url = reverse('signup')
        self.logout_url = reverse('logout')

    def test_auto_profile_creation_signal(self):
        """Verify that a Profile is automatically created when a User is created."""
        self.assertTrue(hasattr(self.user, 'profile'))
        profile = self.user.profile
        self.assertEqual(profile.balance, 0.0)
        self.assertEqual(profile.income, 0.0)
        self.assertEqual(profile.expenses, 0.0)

    def test_unauthenticated_redirect(self):
        """Unauthenticated access to home page should redirect to login page."""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)

    def test_user_login(self):
        """Test user login flow."""
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password
        })
        self.assertRedirects(response, self.home_url)

    def test_add_positive_income_transaction(self):
        """Adding a positive income transaction should increase both balance and total income."""
        self.client.login(username=self.username, password=self.password)
        
        response = self.client.post(self.home_url, {
            'text': 'Salary',
            'amount': '1500.50',
            'expense_type': 'Positive'
        })
        self.assertRedirects(response, self.home_url)

        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.income, 1500.50)
        self.assertEqual(profile.expenses, 0.0)
        self.assertEqual(profile.balance, 1500.50)

        expense = Expense.objects.filter(user=self.user).first()
        self.assertIsNotNone(expense)
        self.assertEqual(expense.name, 'Salary')
        self.assertEqual(expense.amount, 1500.50)
        self.assertEqual(expense.expense_type, 'Positive')

    def test_add_negative_expense_transaction(self):
        """Adding a negative transaction should increase total expenses and decrease balance."""
        self.client.login(username=self.username, password=self.password)

        # First add income of 1000
        self.client.post(self.home_url, {'text': 'Income', 'amount': '1000', 'expense_type': 'Positive'})
        
        # Then add expense of 300
        response = self.client.post(self.home_url, {
            'text': 'Rent Payment',
            'amount': '300.00',
            'expense_type': 'Negative'
        })
        self.assertRedirects(response, self.home_url)

        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.income, 1000.0)
        self.assertEqual(profile.expenses, 300.0)
        self.assertEqual(profile.balance, 700.0)

    def test_delete_transaction(self):
        """Deleting a transaction should recalculate profile income, expenses, and net balance."""
        self.client.login(username=self.username, password=self.password)

        # Add transaction
        self.client.post(self.home_url, {'text': 'Bonus', 'amount': '500', 'expense_type': 'Positive'})
        expense = Expense.objects.filter(user=self.user, name='Bonus').first()
        
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.balance, 500.0)

        # Delete transaction
        delete_url = reverse('delete_expense', kwargs={'pk': expense.pk})
        response = self.client.get(delete_url)
        self.assertRedirects(response, self.home_url)

        profile.refresh_from_db()
        self.assertEqual(profile.income, 0.0)
        self.assertEqual(profile.balance, 0.0)
        self.assertEqual(Expense.objects.filter(user=self.user).count(), 0)

    def test_invalid_amount_input(self):
        """Submitting non-positive or invalid amounts should produce error and not alter profile."""
        self.client.login(username=self.username, password=self.password)

        response = self.client.post(self.home_url, {
            'text': 'Invalid Amount',
            'amount': '-50',
            'expense_type': 'Positive'
        })
        self.assertRedirects(response, self.home_url)
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.balance, 0.0)
