from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView,
)

from auth_satvadev.api.views import ConfirmCodeView, ResetPasswordView

urlpatterns = [
    path('jwt/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('reset-password/', ResetPasswordView.as_view(),
         name='reset_password'),
    path('reset-password/confirm/', ConfirmCodeView.as_view(), name='confirm'),
]
