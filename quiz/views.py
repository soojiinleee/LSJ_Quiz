import random
from datetime import datetime

from rest_framework import viewsets, generics, mixins, permissions
from rest_framework.response import Response
from rest_framework import status

from core.permissions import IsStaffUser
from core.paginations import StandardResultsSetPagination
from question.serializers import QuestionSimpleSerializer
from quiz_attempt.models import QuizAttempt

from .models import Quiz
from .serializers import (
    QuizCreateUpdateSerializer,
    QuizStaffListSerializer,
    QuizStaffDetailSerializer,
    QuizQuestionLinkSerializer,
    QuizUserSerializer,
)


class QuizStaffViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """관리자 : 퀴즈 생성/수정/삭제"""

    queryset = Quiz.objects.all()
    permission_classes = [IsStaffUser]

    def get_serializer_class(self):
        if self.action not in ("destroy",):
            return QuizCreateUpdateSerializer

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.deleted_at = datetime.now()
        instance.save()


class QuizViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """관리자 & 일반 사용자 : 퀴즈 목록 및 상세 조회"""

    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Quiz.objects.filter(is_deleted=False).order_by("-created_at")
        return queryset

    def get_serializer_class(self):
        user = self.request.user
        if self.action == "list":
            return QuizStaffListSerializer if user.is_staff else QuizUserSerializer
        if self.action == "retrieve":
            return QuizStaffDetailSerializer if user.is_staff else QuizUserSerializer


class QuizQuestionLinkAPIView(generics.CreateAPIView):
    """관리자 : 퀴즈-문제 연결"""

    serializer_class = QuizQuestionLinkSerializer
    permission_classes = [IsStaffUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["quiz_id"] = self.kwargs["quiz_id"]
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_201_CREATED)


class QuizQuestionListAPIView(generics.ListAPIView):
    """관리자 & 일반 사용자 : 퀴즈 문제 목록 조회"""

    serializer_class = QuestionSimpleSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        quiz_id = self.kwargs["quiz_id"]
        quiz = Quiz.objects.get(pk=quiz_id)
        user = self.request.user

        # 1. 퀴즈 응시한 경우 -> 저장한 문제 순서
        quiz_attempt = QuizAttempt.objects.filter(
            user_id=user.id, quiz_id=quiz_id
        ).first()
        if quiz_attempt:
            attempt_questions = quiz_attempt.questions.select_related(
                "question"
            ).order_by("order_index")
            return [aq.question for aq in attempt_questions]

        # 2. 퀴즈 응시하지 않은 경우 -> 랜덤 출제
        related_questions = list(
            quiz.related_questions.select_related("question").all()
        )
        question_count = quiz.question_count

        # 퀴즈 출제 문제 랜덤 추출
        selected_questions = random.sample(related_questions, question_count)

        # 문제 랜덤 정렬
        if quiz.is_random_question:
            random.shuffle(selected_questions)

        return [quiz_question.question for quiz_question in selected_questions]
