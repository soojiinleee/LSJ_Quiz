import shortuuid

from django.db import models
from django.contrib.auth.models import User

from core.models import TimeStampedMixin
from question.models import Question
from quiz.models import Quiz


def generate_quiz_attempt_code():
    """퀴즈 응시 코드 생성"""
    return shortuuid.ShortUUID().random(length=5).upper()


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    attempt_code = models.CharField(
        default=generate_quiz_attempt_code(),
        max_length=7,
        unique=True,
        verbose_name="퀴즈 응시 코드"
    )
    attempt_question_count = models.PositiveIntegerField(default=0, verbose_name='퀴즈 응시 시점의 출제 문제 수')
    correct_count = models.PositiveIntegerField(null=True, blank=True, verbose_name='맞은 문제 개수')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='퀴즈 응시 일시')
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='퀴즈 제출 일시')
    question = models.ManyToManyField(
        Question,
        through='quiz_attempt.QuizAttemptQuestion',
        verbose_name="응시한 퀴즈에 출제된 문제"
    )

    def __str__(self):
        return f"{self.attempt_code} - {self.user.username}"


    class Meta:
        unique_together = ('user', 'quiz')
        db_table = 'quiz_attempt'
        verbose_name = '퀴즈 응시'
        verbose_name_plural = '퀴즈 응시'


class QuizAttemptQuestion(TimeStampedMixin):
    # TODO 퀴즈 응시 답안 저장 여부 고민 필요
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='attempt_questions'
    )
    order_index = models.PositiveIntegerField(verbose_name='응시 시점의 문제 순서')

    def __str__(self):
        return f"Attempt {self.attempt_id} - Q{self.question.id}"

    class Meta:
        unique_together = ('attempt', 'question')
        db_table = 'quiz_attempt_question'
        verbose_name = '퀴즈 출제 문제'
        verbose_name_plural = '퀴즈 출제 문제'
