from django.contrib.auth.models import User
from django.db import models

from core.models import TimeStampedMixin
from question.models import Question

class Quiz(TimeStampedMixin):
    title = models.CharField(max_length=255)
    is_random_question = models.BooleanField(default=False)
    is_random_choice = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quiz'
    )
    questions = models.ManyToManyField(
        'question.Question',
        through='quiz.QuizQuestion',
        blank=True,
        verbose_name='퀴즈 문제'
    )

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'quiz'
        verbose_name = '퀴즈'
        verbose_name_plural = '퀴즈'


class QuizQuestion(TimeStampedMixin):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='related_questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='related_quizzes')

    class Meta:
        db_table = 'quiz_question'
        unique_together = ('quiz', 'question')
        verbose_name = '퀴즈-문제'
        verbose_name_plural = '퀴즈-문제'