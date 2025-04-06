from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.contrib import admin
from django.urls import path, include

schema_view = get_schema_view(
    openapi.Info(
        title="퀴즈 서비스 API",
        default_version="v1",
        description="관리자 및 사용자용 퀴즈 플랫폼 API",
    ),
    public=True,
)

urlpatterns = [
    path("swagger/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("admin/", admin.site.urls),
    path("quiz/", include("quiz.urls")),
    path("question/", include("question.urls")),
    path("attempt/", include("quiz_attempt.urls")),
]
