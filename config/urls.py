from drf_spectacular.views import SpectacularJSONAPIView
from drf_spectacular.views import SpectacularRedocView
from drf_spectacular.views import SpectacularSwaggerView

from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("quiz/", include("quiz.urls")),
    path("question/", include("question.urls")),
    path("attempt/", include("quiz_attempt.urls")),
]

if settings.DEBUG:
    urlpatterns = [
        # swagger 문서
        path("docs/json/", SpectacularJSONAPIView.as_view(), name="schema-json"),
        path(
            "docs/swagger/",
            SpectacularSwaggerView.as_view(url_name="schema-json"),
            name="swagger-ui",
        ),
        path(
            "docs/redoc/",
            SpectacularRedocView.as_view(url_name="schema-json"),
            name="redoc",
        ),
    ] + urlpatterns
