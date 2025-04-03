from rest_framework import viewsets, mixins
from core.permissions import IsStaffUser
from .models import Quiz
from .serializers import QuizCreateUpdateSerializer


class QuizManageViewSet(mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):

    queryset = Quiz.objects.all()
    serializer_class = QuizCreateUpdateSerializer
    permission_classes = [IsStaffUser]
