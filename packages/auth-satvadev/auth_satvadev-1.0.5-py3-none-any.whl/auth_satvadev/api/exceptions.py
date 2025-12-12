from rest_framework import status
from rest_framework.exceptions import APIException


class CodeDoesNotMatchError(APIException):
    """Ошибка ввода кода подтверждения"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Verification code does not match'
    default_code = 'CodeDoesNotMatchError'
