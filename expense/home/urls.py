from django.urls import path
from .views import home, delete_expense, signup_view, login_view, logout_view

urlpatterns = [
    path('', home, name='home'),
    path('delete/<int:pk>/', delete_expense, name='delete_expense'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]