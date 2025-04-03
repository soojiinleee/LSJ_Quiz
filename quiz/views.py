from rest_framework import viewsets, mixins, generics
from rest_framework.response import Response
from rest_framework import status

from core.permissions import IsStaffUser
from .models import Quiz
from .serializers import QuizCreateUpdateSerializer, QuizQuestionLinkSerializer


class QuizManageViewSet(mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):

    queryset = Quiz.objects.all()
    serializer_class = QuizCreateUpdateSerializer
    permission_classes = [IsStaffUser]


class QuizQuestionLinkAPIView(generics.CreateAPIView):
    serializer_class = QuizQuestionLinkSerializer
    permission_classes = [IsStaffUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['quiz_id'] = self.kwargs['quiz_id']
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_201_CREATED)