from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.contrib import admin
from django.urls import path, include, re_path

# from rest_framework import permissions
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("authentication.urls")),
    path("expenses/", include("expenses.urls")),
]

# Swagger Configuration
# schema_view = get_schema_view(
#     openapi.Info(
#         title="Income Expense API",
#         default_version="v1",
#         description="API for Expense Tracking",
#         terms_of_service="https://www.google.com/policies/terms/",
#         contact=openapi.Contact(email="contact@snippets.local"),
#         license=openapi.License(name="BSD License"),
#     ),
#     public=True,
#     permission_classes=[permissions.AllowAny],
# )

# urlpatterns += [
#     # re_path(
#     #     r"^swagger(?P<format>\.json|\.yaml)$",
#     #     schema_view.without_ui(cache_timeout=0),
#     #     name="schema-json",
#     # ),
#     re_path(
#         # r"^swagger/$",
#         r"",
#         schema_view.with_ui("swagger", cache_timeout=0),
#         name="schema-swagger-ui",
#     ),
#     # re_path(
#     #     r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
#     # ),
# ]

urlpatterns += [
    path("docs/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
