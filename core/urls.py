
from django.urls import path

from .views import SignupView, LoginView, ProfileView, UpdatePasswordView

urlpatterns = [
    path('signup', SignupView.as_view(), name='signup-view'),
    path('login', LoginView.as_view(), name='login-view'),
    path('profile', ProfileView.as_view(), name='profile-view'),
    path('update_password', UpdatePasswordView.as_view(), name='update_password-view'),

]
