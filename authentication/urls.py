from django.urls import path
from .views import (
    RegisterView,
    VerifyEmail,
    LoginView,
    PasswordResetRequest,
    PasswordResetConfirm,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-email/", VerifyEmail.as_view(), name="verify-email"),
    path("login/", LoginView.as_view(), name="login"),
    path(
        "password-reset-request/",
        PasswordResetRequest.as_view(),
        name="password-reset-request",
    ),
    path(
        "password-reset-confirm/",
        PasswordResetConfirm.as_view(),
        name="password-reset-confirm",
    ),
]
