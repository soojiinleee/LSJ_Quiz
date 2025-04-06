from rest_framework.routers import DefaultRouter
from .views import QuestionViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r"", QuestionViewSet, basename="questions")

urlpatterns = [
    path("", include(router.urls)),
]
