from django.urls import path

from .views import (
    QuizAttemptAPIView, QuizAttemptQuestionDetailAPIView,
    QuizAttemptChoiceAPIView,
    # QuizAttemptChoiceViewSet
    )

urlpatterns = [
    path('', QuizAttemptAPIView.as_view(), name='quiz-attempt'),
    path('question/<int:question_id>/', QuizAttemptQuestionDetailAPIView.as_view(), name='quiz-attempt-question'),
    path('choice/', QuizAttemptChoiceAPIView.as_view(), name='attempt-choice'),
    # path('', QuizSubmissionAPIView.as_view(), name='quiz-submission'),
]