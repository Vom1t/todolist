

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from core.fields import PasswordField
from core.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    """Сериализатор создания пользователя"""

    password = PasswordField(required=True)
    password_repeat = PasswordField(required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'password_repeat'
        )

    def validate(self, attrs: dict) -> dict:
        """Функция проверки введенных паролей"""

        if attrs['password'] != attrs['password_repeat']:
            raise ValidationError({'password_repeat': 'Passwords must match'})
        return attrs

    def create(self, validated_data: dict) -> User:
        """Функция удаляет 'password_repeat', хэширует пароль и создает пользователя"""

        del validated_data['password_repeat']
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class LoginSerializer(serializers.ModelSerializer):
    """Сериализатор проверки пользователя на входе"""

    username = serializers.CharField(required=True)
    password = PasswordField(required=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password'
        )
        read_only_fields = (
            'id',
            'first_name',
            'last_name',
            'email'
        )

    def create(self, validated_data: dict) -> User:
        """Функция аутентификации пользователя"""

        if not (user := authenticate(
                username=validated_data['username'],
                password=validated_data['password']
        )):
            raise AuthenticationFailed
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email'
        )


class UpdatePasswordSerializer(serializers.Serializer):
    """Сериализатор смены пароля"""

    old_password = serializers.CharField(required=True, style={'input_type': 'password'}, write_only=True)
    new_password = PasswordField(required=True)

    def validate_old_password(self, value):
        """Функция проверяет совпадения 'old_password' с действующим паролем"""

        if not self.instance.check_password(value):
            raise ValidationError('Password is incorrect!')

        return value

    def update(self, instance: User, validated_data: dict) -> User:
        """Функция хэширует 'new_password' и обновляет пароль в БД"""

        instance.set_password(validated_data['new_password'])
        instance.save(update_fields=('password',))
        return instance

    def create(self, validated_data):
        raise NotImplementedError
