from rest_framework import generics, permissions, mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from question.serializers import QuestionDetailWithChoicesSerializer
from .serializers import QuizAttemptCreateSerializer, QuizAttemptChoiceCreateSerializer, QuizAttemptChoiceUpdateSerializer
from .models import QuizAttempt, QuizAttemptQuestion


class QuizAttemptAPIView(generics.CreateAPIView):
    """퀴즈 응시"""
    serializer_class = QuizAttemptCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class QuizAttemptQuestionDetailAPIView(generics.RetrieveAPIView):
    """퀴즈 출제 문제 상세 조회"""
    serializer_class = QuestionDetailWithChoicesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        quiz_id = self.request.query_params.get('quiz_id', None)
        question_id = self.kwargs['question_id']

        if not quiz_id:
            raise ValidationError('quiz_id 쿼리 파라미터가 필요합니다.')

        quiz_attempt = get_object_or_404(QuizAttempt, user=user, quiz_id=quiz_id)
        self.quiz_attempt = quiz_attempt

        attempt_question = quiz_attempt.questions.select_related('question').get(question_id=question_id)
        return attempt_question.question

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['quiz_attempt'] = getattr(self, 'quiz_attempt', None)
        return context


class QuizAttemptChoiceCreateAPIView(generics.CreateAPIView):
    serializer_class = QuizAttemptChoiceCreateSerializer
    permission_classes = [permissions.IsAuthenticated]



# class QuizAttemptChoiceViewSet(mixins.CreateModelMixin,
#                                       mixins.UpdateModelMixin,
#                                       viewsets.GenericViewSet):
#     """선택지 순서 저장(Post) / 선택한 선택지 수정 : 정답 선택(Put) API"""
#
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_serializer_class(self):
#         if self.request.method == 'POST':
#             return QuizAttemptChoiceCreateSerializer
#         elif self.request.method == 'PUT':
#             return QuizAttemptChoiceUpdateSerializer
#
#     def put(self, request, *args, **kwargs):
#         attempt_question = self.get_object()
#         serializer = self.get_serializer(data=request.data, context={'attempt_question': attempt_question})
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)

