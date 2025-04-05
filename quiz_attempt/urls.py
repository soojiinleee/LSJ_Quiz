from django.urls import path

from .views import QuizAttemptAPIView


urlpatterns = [
    path('', QuizAttemptAPIView.as_view(), name='quiz-attempt'),
    # path('', QuizSubmissionAPIView.as_view(), name='quiz-submission'),

]