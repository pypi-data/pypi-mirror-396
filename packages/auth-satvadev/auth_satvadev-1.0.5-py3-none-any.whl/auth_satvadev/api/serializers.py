from django.contrib.auth import get_user_model
from rest_framework import serializers


class EmailResetPasswordSerializer(serializers.Serializer):
    """Сериалайзер сброса пароля"""
    email = serializers.EmailField()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        """Получение существующего юзера"""
        email = obj.get('email')
        user_model = get_user_model()
        user = user_model.objects.get(email=email)

        return user


class EmailConfirmCodeSerializer(serializers.Serializer):
    """Сериалайзер проверки кода, отправленного на почту"""
    email = serializers.EmailField()
    code = serializers.IntegerField()
    password = serializers.CharField()
