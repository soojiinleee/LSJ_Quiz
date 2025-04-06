from rest_framework import generics, permissions, status
from rest_framework.response import Response

from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from question.serializers import QuestionDetailWithChoicesSerializer
from quiz.models import QuizQuestion
from .serializers import (
    QuizAttemptCreateSerializer,
    QuizAttemptChoiceCreateSerializer,
    QuizAttemptChoiceUpdateSerializer,
    QuizSubmissionSerializer,
)
from .models import QuizAttempt
from .schemas import (
    ATTEMPT_QUIZ_CREATE_SCHEMA,
    ATTEMPT_QUESTION_SCHEMA,
    ATTEMPT_CHOICE_SCHEMA_View,
    QUIZ_SUBMISSION_SCHEMA_View,
)


@ATTEMPT_QUIZ_CREATE_SCHEMA
class QuizAttemptAPIView(generics.CreateAPIView):
    """퀴즈 응시 및 출제 문제 순서 저장"""

    serializer_class = QuizAttemptCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


@ATTEMPT_QUESTION_SCHEMA
class QuizAttemptQuestionDetailAPIView(generics.RetrieveAPIView):
    """퀴즈 출제 문제 상세 조회"""

    serializer_class = QuestionDetailWithChoicesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        quiz_id = self.request.query_params.get("quiz_id", None)
        question_id = self.kwargs["question_id"]

        if not quiz_id:
            raise ValidationError("quiz_id 쿼리 파라미터가 필요합니다.")

        quiz_question = get_object_or_404(
            QuizQuestion, quiz_id=quiz_id, question_id=question_id
        )
        return quiz_question.question


@ATTEMPT_CHOICE_SCHEMA_View
class QuizAttemptChoiceAPIView(generics.CreateAPIView, generics.UpdateAPIView):
    """풀이 문제 선택지 순서(POST) & 고른 선택지 저장(PUT)"""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        quiz_id = self.request.data.get("quiz_id")
        question_id = self.request.data.get("question_id")

        quiz_attempt = get_object_or_404(QuizAttempt, user=user, quiz_id=quiz_id)
        attempt_question = quiz_attempt.questions.get(question_id=question_id)
        attempt_choice = attempt_question.choices.all()  # QuizAttemptChoice 쿼리셋

        return attempt_choice

    def get_serializer_class(self):
        if self.request.method == "POST":
            return QuizAttemptChoiceCreateSerializer
        elif self.request.method == "PUT":
            return QuizAttemptChoiceUpdateSerializer

    def put(self, request, *args, **kwargs):
        # 1. 현재 문제에 연결된 모든 선택지 가져오기
        queryset = self.get_queryset()

        # 2. 기존 선택 여부 전체 초기화 (모두 False)
        queryset.update(is_selected=False)

        # 3. instance 찾기
        selected_choice_id = request.data.get("selected_choice_id")
        instance = queryset.get(choice_id=selected_choice_id)

        # 4. 선택한 정답으로 변경
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


@QUIZ_SUBMISSION_SCHEMA_View
class QuizSubmissionAPIView(generics.UpdateAPIView):
    """퀴즈 제출"""

    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        quiz_id = request.query_params.get("quiz_id")

        if not quiz_id:
            return Response({"detail": "quiz_id가 필요합니다."}, status=400)

        # 유저가 해당 퀴즈에 이미 응시한 기록 가져오기
        quiz_attempt = get_object_or_404(QuizAttempt, user=user, quiz_id=quiz_id)

        # 제출 처리 (submitted_at, 정답 여부 등)
        serializer = QuizSubmissionSerializer(quiz_attempt, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=200)
