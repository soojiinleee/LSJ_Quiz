import random

from rest_framework import viewsets, generics, mixins
from rest_framework.response import Response
from rest_framework import status

from core.permissions import IsStaffUser
from core.paginations import StandardResultsSetPagination
from question.serializers import QuestionSimpleSerializer
from quiz_attempt.models import QuizAttempt, QuizAttemptQuestion

from .models import Quiz
from .serializers import (
    QuizCreateUpdateSerializer,
    QuizStaffListSerializer,
    QuizStaffDetailSerializer,
    QuizQuestionLinkSerializer
)


class QuizStaffViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffUser]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        query_set = Quiz.objects.prefetch_related('related_questions').all().order_by('-created_at')
        return query_set

    def get_serializer_class(self):
        if self.action == 'list':
            return QuizStaffListSerializer
        if self.action == 'retrieve':
            # TODO 테스트 코드 작성
            return QuizStaffDetailSerializer
        if self.action == 'destroy':
            # TODO 퀴즈 삭제 -> quiz_question 내용도 삭제 처리
            pass
        return QuizCreateUpdateSerializer


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


class QuizQuestionListAPIView(generics.ListAPIView):
    serializer_class = QuestionSimpleSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        quiz_id = self.kwargs['quiz_id']
        quiz = Quiz.objects.get(pk=quiz_id)
        user = self.request.user

        # 1. 퀴즈 응시한 경우 -> 저장한 문제 순서
        quiz_attempt = QuizAttempt.objects.filter(user_id=user.id, quiz_id=quiz_id).first()
        if quiz_attempt:
            attempt_questions = quiz_attempt.questions.select_related('question').order_by('order_index')
            return [aq.question for aq in attempt_questions]

        # 2. 퀴즈 응시하지 않은 경우 -> 랜덤 출제
        related_questions = list(quiz.related_questions.select_related('question').all())
        question_count = quiz.question_count

        # 퀴즈 출제 문제 랜덤 추출
        selected_questions = random.sample(related_questions, question_count)

        # 문제 랜덤 정렬 (TODO : 테스트 코드 작성 - test_quiz_question_random_order)
        if quiz.is_random_question:
            random.shuffle(selected_questions)

        # Question 객체로 변환
        return [quiz_question.question for quiz_question in selected_questions]
