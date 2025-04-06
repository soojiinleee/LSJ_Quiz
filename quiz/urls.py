from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QuizStaffViewSet,
    QuizViewSet,
    QuizQuestionLinkAPIView,
    QuizQuestionListAPIView,
)

router = DefaultRouter()
router.register(r"read", QuizViewSet, basename="quiz")
router.register(r"staff", QuizStaffViewSet, basename="quiz-staff")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:quiz_id>/question-link/",
        QuizQuestionLinkAPIView.as_view(),
        name="quiz-question-link",
    ),
    path(
        "<int:quiz_id>/question/",
        QuizQuestionListAPIView.as_view(),
        name="quiz-question",
    ),
]
