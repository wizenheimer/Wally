from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
import jwt
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import (
    force_str,
    smart_str,
    smart_bytes,
    DjangoUnicodeDecodeError,
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.social_serializers import TwitterLoginSerializer
from dj_rest_auth.registration.views import SocialLoginView

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    VerifyEmailSerializer,
    PasswordResetSerializer,
    GeneratePasswordResetToken,
)
from .models import User


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data

        user = User.objects.get(email=user_data["email"])
        token = RefreshToken.for_user(user)

        current_site = get_current_site(request).domain
        relativeLink = reverse("verify-email")

        absurl = (
            "http://" + current_site + relativeLink + f"?token={token.access_token}"
        )

        send_mail(
            subject="Verify email",
            message=f"Get Started:{absurl}",
            from_email="djangomailer@mail.com",
            recipient_list=[
                user.email,
            ],
        )

        return Response(user_data, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyEmail(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="token",
                type=OpenApiTypes.STR,
                required=True,
                location=OpenApiParameter.QUERY,
                description="Email Verification Token",
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")

            user = User.objects.get(id=payload["user_id"])

            user.is_verified = True
            user.save()

            return Response(
                {"email": "email successfully activated."},
                status=status.HTTP_200_OK,
            )
        except jwt.DecodeError:
            return Response(
                {"error": "Invalid Token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except jwt.ExpiredSignatureError:
            return Response(
                {"error": "Activation Expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PasswordResetConfirm(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.data)
        uidb64 = serializer.data.get("uidb64")
        password = serializer.data.get("password")

        uid = smart_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
        user.is_active = True
        user.set_password(password)
        user.save()

        return Response({"message": "Password changed successfully."})


class PasswordResetRequest(generics.GenericAPIView):
    serializer_class = GeneratePasswordResetToken

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")
        print(email)
        user = User.objects.get(email=email)
        user.is_active = False
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user=user)

        current_site = get_current_site(request).domain
        relativeLink = reverse("password-reset-confirm")

        absurl = (
            "http://" + current_site + relativeLink + f"?uidb64={uidb64}&token={token}/"
        )

        send_mail(
            subject="Verify email",
            message=f"Link:{absurl}",
            from_email="djangomailer@mail.com",
            recipient_list=[
                user.email,
            ],
        )

        return Response({"message": "Password reset request sent successfully."})


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="access_token",
            type=OpenApiTypes.STR,
            required=True,
            location=OpenApiParameter.QUERY,
            description="Access Token",
        ),
        OpenApiParameter(
            name="code",
            type=OpenApiTypes.STR,
            required=True,
            location=OpenApiParameter.QUERY,
            description="code",
        ),
        OpenApiParameter(
            name="id_token",
            type=OpenApiTypes.STR,
            required=True,
            location=OpenApiParameter.QUERY,
            description="id_token",
        ),
    ]
)
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://127.0.0.1:8000/accounts/google/login/callback/"
    client_class = OAuth2Client


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="access_token",
            type=OpenApiTypes.STR,
            required=True,
            location=OpenApiParameter.QUERY,
            description="Access Token",
        ),
        OpenApiParameter(
            name="code",
            type=OpenApiTypes.STR,
            required=True,
            location=OpenApiParameter.QUERY,
            description="code",
        ),
        OpenApiParameter(
            name="id_token",
            type=OpenApiTypes.STR,
            required=True,
            location=OpenApiParameter.QUERY,
            description="id_token",
        ),
    ]
)
class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="access_token",
            type=OpenApiTypes.STR,
            required=True,
            location=OpenApiParameter.QUERY,
            description="Access Token",
        ),
        OpenApiParameter(
            name="token_secret",
            type=OpenApiTypes.STR,
            required=True,
            location=OpenApiParameter.QUERY,
            description="code",
        ),
    ]
)
class TwitterLogin(SocialLoginView):
    serializer_class = TwitterLoginSerializer
    adapter_class = TwitterOAuthAdapter
