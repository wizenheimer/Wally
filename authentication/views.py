from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
import jwt

# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg import openapi
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    VerifyEmailSerializer,
)
from .models import User
from .renderers import UserRenderer


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)

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


# class VerifyEmail(generics.GenericAPIView):
#     serializer_class = VerifyEmailSerializer

#     @extend_schema(
#         parameters=[
#             OpenApiParameter(
#                 name="token",
#                 type=OpenApiTypes.STR,
#                 required=True,
#                 location=OpenApiParameter.QUERY,
#                 description="Email Verification Token",
#             ),
#         ]
#     )
#     def get(self, request):
#         token = request.GET.get("token")
#         try:
#             payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")

#             user = User.objects.get(id=payload["user_id"])

#             user.is_verified = True

#             return Response(
#                 {"email": "email successfully activated."},
#                 status=status.HTTP_200_OK,
#             )
#         except jwt.DecodeError:
#             return Response(
#                 {"error": "Invalid Token."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         except jwt.ExpiredSignatureError:
#             return Response(
#                 {"error": "Activation Expired."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )


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
