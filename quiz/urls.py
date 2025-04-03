from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizManageViewSet

router = DefaultRouter()
router.register(r'manage', QuizManageViewSet, basename='quiz-manage')

urlpatterns = [
    path('', include(router.urls)),
]
