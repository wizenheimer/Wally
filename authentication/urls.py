from django.urls import path
from .views import RegisterView, VerifyEmail, LoginView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-email/", VerifyEmail.as_view(), name="verify-email"),
    path("login/", LoginView.as_view(), name="login"),
]
