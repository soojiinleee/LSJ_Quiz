from rest_framework import generics, permissions, mixins, viewsets, status
from rest_framework.response import Response

from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from question.serializers import QuestionDetailWithChoicesSerializer
from .serializers import QuizAttemptCreateSerializer, QuizAttemptChoiceCreateSerializer, QuizAttemptChoiceUpdateSerializer
from .models import QuizAttempt, QuizAttemptChoice


class QuizAttemptAPIView(generics.CreateAPIView):
    """퀴즈 응시 및 출제 문제 순서 저장"""
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


class QuizAttemptChoiceAPIView(generics.CreateAPIView,
                               generics.UpdateAPIView):

    """풀이 문제 선택지 순서(POST) & 고른 선택지 저장(PUT)"""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        quiz_id = self.request.data.get('quiz_id')
        question_id = self.request.data.get('question_id')

        quiz_attempt = get_object_or_404(QuizAttempt, user=user, quiz_id=quiz_id)
        attempt_question = quiz_attempt.questions.get(question_id=question_id)
        attempt_choice = attempt_question.choices.all() # QuizAttemptChoice 쿼리셋

        return attempt_choice

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QuizAttemptChoiceCreateSerializer
        elif self.request.method == 'PUT':
            return QuizAttemptChoiceUpdateSerializer

    def put(self, request, *args, **kwargs):
        # 1. 현재 문제에 연결된 모든 선택지 가져오기
        queryset = self.get_queryset()

        # 2. 기존 선택 여부 전체 초기화 (모두 False)
        queryset.update(is_selected=False)

        # 3. instance 찾기
        selected_choice_id = request.data.get('selected_choice_id')
        instance = queryset.get(choice_id=selected_choice_id)

        # 4. 선택한 정답으로 변경
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)