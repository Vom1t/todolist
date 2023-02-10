
from django.urls import path

from .views import SignupView, LoginView, ProfileView, UpdatePasswordView

urlpatterns = [
    path('signup', SignupView.as_view(), name='signup'),
    path('login', LoginView.as_view(), name='login'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('update_password', UpdatePasswordView.as_view(), name='update-password'),
]
