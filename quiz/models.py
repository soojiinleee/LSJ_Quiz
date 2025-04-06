from django.contrib.auth.models import User
from django.db import models

from core.models import TimeStampedMixin
from question.models import Question

class Quiz(TimeStampedMixin):
    title = models.CharField(max_length=255, verbose_name="퀴즈 내용")
    question_count = models.PositiveIntegerField(default=0, verbose_name="퀴즈에 노출될 문제 개수")
    is_random_question = models.BooleanField(default=False, verbose_name="문제 랜덤 배치")
    is_random_choice = models.BooleanField(default=False, verbose_name="선택지 랜덤 배치")
    is_deleted = models.BooleanField(default=False, verbose_name='삭제 여부')
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_quiz',
        verbose_name="퀴즈 생성한 관리자"
    )
    questions = models.ManyToManyField(
        'question.Question',
        through='quiz.QuizQuestion',
        blank=True,
        verbose_name='퀴즈 문제'
    )
    attempt_user = models.ManyToManyField(
        User,
        through='quiz_attempt.QuizAttempt',
        related_name='attempted_quiz',
        verbose_name="퀴즈 응시한 유저"
    )
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='삭제 시점')

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