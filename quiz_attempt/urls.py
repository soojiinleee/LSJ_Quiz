from django.urls import path

from .views import (
    QuizAttemptAPIView,
    QuizAttemptQuestionDetailAPIView,
    QuizAttemptChoiceAPIView,
    QuizSubmissionAPIView
    )

urlpatterns = [
    path('', QuizAttemptAPIView.as_view(), name='quiz-attempt'),
    path('question/<int:question_id>/', QuizAttemptQuestionDetailAPIView.as_view(), name='quiz-attempt-question'),
    path('choice/', QuizAttemptChoiceAPIView.as_view(), name='attempt-choice'),
    path('submission/', QuizSubmissionAPIView.as_view(), name='quiz-submission'),
]