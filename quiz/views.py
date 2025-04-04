import random
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework import status

from core.permissions import IsStaffUser
from core.paginations import StandardResultsSetPagination
from question.serializers import QuestionSimpleSerializer
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
        related_questions = list(quiz.related_questions.select_related('question').all())
        question_count = quiz.question_count

        # 퀴즈 출제 문제 랜덤 추출
        selected_questions = random.sample(related_questions, question_count)

        # 문제 랜덤 정렬 (TODO : 테스트 코드 작성 - test_quiz_question_random_order)
        if quiz.is_random_question:
            random.shuffle(selected_questions)

        # Question 객체로 변환
        questions = [quiz_question.question for quiz_question in selected_questions]

        return questions


# TODO : 일반 사용자 (응시 CRUD)
# class QuizUserViewSet(mixins.ListModelMixin,
#                   mixins.RetrieveModelMixin,
#                   viewsets.GenericViewSet):
