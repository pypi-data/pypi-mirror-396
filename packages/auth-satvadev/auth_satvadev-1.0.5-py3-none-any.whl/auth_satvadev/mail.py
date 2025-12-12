from django.template import Template
from mail_satvadev.messages import BaseMail


class ResetPasswordMail(BaseMail):
    """Класс генерирует текст письма с проверочным кодом"""
    subject_template = Template('Сброс пароля')
    template = Template('Проверочный код: {{ code }}')
