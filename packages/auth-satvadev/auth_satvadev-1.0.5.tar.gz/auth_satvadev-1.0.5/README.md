# Django приложение аутентификации

## Конфигурация
Подключение приложения
```python
INSTALLED_APPS = [
    'auth_satvadev',
]
```

## Использование классов аутентификации
Для использования необходимо задать переменную в settings.py:
```python
SENDER_CLASS = 'path_to_sender_class.SenderClassName'
```
, где SenderClassName название класса для отправления и валидации кода подтверждения из списка:
```
'auth_satvadev.senders.MailSender',
```

Также, необходимо добавить URL's аутентификации в urls.py проекта:
```python
urlpatterns = [
    ...
    path(
        'api/auth-satvadev/',
        include(('auth_satvadev.api.urls', 'auth_satvadev'))
    ),
    ...
]
```

Для запросов авторизации используются пути:
- 'api/auth-satvadev/jwt/' - для получения JWT токена
- 'api/auth-satvadev/jwt/refresh/' - обновления JWT токена
- 'api/auth-satvadev/reset-password/' - для запроса на восстановление пароля
- 'api/auth-satvadev/reset-password/confirm/' - для проверки кода подтверждения
