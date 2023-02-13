from django.contrib.auth import login, logout
from rest_framework import generics, status, permissions
from rest_framework.response import Response

from core.models import User
from core.serializers import CreateUserSerializer, LoginSerializer, ProfileSerializer, UpdatePasswordSerializer


class SignupView(generics.CreateAPIView):
    """Вью регистрации пользователя"""

    serializer_class = CreateUserSerializer


class LoginView(generics.CreateAPIView):
    """Вью входа пользователя"""
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        """Функция логина пользователя"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        login(request=self.request, user=serializer.save())


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    """Вью отображения, редактирования и выхода пользователя"""

    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Функция возвращает пользователя из БД"""

        return self.request.user

    def perform_destroy(self, instance):
        """Функция выхода из аккаунта"""

        logout(self.request)


class UpdatePasswordView(generics.UpdateAPIView):
    """Вью смены пароля"""

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UpdatePasswordSerializer

    def get_object(self):
        """Функция возвращает пользователя из БД"""

        return self.request.user
