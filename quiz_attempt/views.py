from rest_framework import generics, permissions
from .serializers import QuizAttemptCreateSerializer

# 일반 유저의 퀴즈 목록 조회는 어느 도메인? attempt or quiz

class QuizAttemptAPIView(generics.CreateAPIView):
    serializer_class = QuizAttemptCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class QuizSubmissionAPIView(generics.CreateAPIView):
    # 일반 유저(로그인 상태) - 답안 저장
    pass