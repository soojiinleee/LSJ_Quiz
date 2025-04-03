from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizManageViewSet, QuizQuestionLinkAPIView

router = DefaultRouter()
router.register(r'manage', QuizManageViewSet, basename='quiz-manage')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:quiz_id>/question/', QuizQuestionLinkAPIView.as_view(), name='quiz-question-link'),
]
