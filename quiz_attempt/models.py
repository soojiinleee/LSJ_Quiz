import shortuuid

from django.db import models
from django.contrib.auth.models import User

from core.models import TimeStampedMixin
from question.models import Question, Choice
from quiz.models import Quiz


def generate_quiz_attempt_code():
    """퀴즈 응시 코드 생성"""
    return shortuuid.ShortUUID().random(length=5).upper()


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="quiz_attempts"
    )
    attempt_code = models.CharField(
        max_length=7,
        unique=True,
        verbose_name="퀴즈 응시 코드",
    )
    attempt_question_count = models.PositiveIntegerField(
        default=0, verbose_name="퀴즈 응시 시점의 출제 문제 수"
    )
    correct_count = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="맞은 문제 개수"
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="퀴즈 응시 일시")
    submitted_at = models.DateTimeField(
        null=True, blank=True, verbose_name="퀴즈 제출 일시"
    )
    question = models.ManyToManyField(
        Question,
        through="quiz_attempt.QuizAttemptQuestion",
        verbose_name="응시한 퀴즈에 출제된 문제",
    )

    def __str__(self):
        return f"{self.attempt_code} - {self.user.username}"

    class Meta:
        unique_together = ("user", "quiz")
        db_table = "quiz_attempt"
        verbose_name = "퀴즈 응시"
        verbose_name_plural = "퀴즈 응시"


class QuizAttemptQuestion(TimeStampedMixin):
    attempt = models.ForeignKey(
        QuizAttempt, on_delete=models.CASCADE, related_name="questions"
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="attempt_questions"
    )
    order_index = models.PositiveIntegerField(verbose_name="응시 시점의 문제 순서")
    is_correct = models.BooleanField(default=False, verbose_name="정답 여부")

    def __str__(self):
        return f"Attempt {self.attempt_id} - Q{self.question.id}"

    class Meta:
        unique_together = ("attempt", "question")
        db_table = "quiz_attempt_question"
        verbose_name = "퀴즈 출제 문제"
        verbose_name_plural = "퀴즈 출제 문제"


class QuizAttemptChoice(TimeStampedMixin):
    attempt_question = models.ForeignKey(
        "quiz_attempt.QuizAttemptQuestion",
        on_delete=models.CASCADE,
        related_name="choices",
        verbose_name="응시 문제",
    )
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, verbose_name="선택지")
    order_index = models.PositiveIntegerField(verbose_name="선택지 순서")
    is_selected = models.BooleanField(default=False, verbose_name="유저 선택 여부")

    def __str__(self):
        return f"AttemptQuestion {self.attempt_question_id} - Choice {self.choice_id}"

    class Meta:
        db_table = "quiz_attempt_choice"
        verbose_name = "퀴즈 응시 선택지"
        verbose_name_plural = "퀴즈 응시 선택지"
        unique_together = ("attempt_question", "choice")
