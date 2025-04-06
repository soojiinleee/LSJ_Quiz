from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (QuizAttemptAPIView, QuizAttemptQuestionDetailAPIView, QuizAttemptChoiceCreateAPIView,
                    # QuizAttemptChoiceViewSet
    )

# router = DefaultRouter()
# router.register(r'choice', QuizAttemptChoiceViewSet, basename='attempt-choice')

urlpatterns = [
    path('', QuizAttemptAPIView.as_view(), name='quiz-attempt'),
    path('question/<int:question_id>/', QuizAttemptQuestionDetailAPIView.as_view(), name='quiz-attempt-question'),
    path('choice/', QuizAttemptChoiceCreateAPIView.as_view(), name='attempt-choice'),
    # path('', QuizSubmissionAPIView.as_view(), name='quiz-submission'),
]