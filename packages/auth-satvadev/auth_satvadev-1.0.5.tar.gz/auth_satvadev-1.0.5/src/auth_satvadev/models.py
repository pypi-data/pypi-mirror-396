from django.contrib.auth import get_user_model
from django.db.models import (
    CASCADE, Model, OneToOneField, PositiveIntegerField,
)


class AbstractVerificationCode(Model):
    """Абстрактная модель для хранения email и проверочного кода"""
    user = OneToOneField(get_user_model(), on_delete=CASCADE, primary_key=True)
    code = PositiveIntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        """Строковое представление кодов подтверждения"""
        return f'Verification code for user #{self.user_id}: {self.code}'


class VerificationCode(AbstractVerificationCode):
    """Модель хранит email пользователя и проверочный код"""
