from django.db import models

from core.models import TimeStampedMixin


class Question(TimeStampedMixin):
    text = models.TextField(null=False, blank=False, verbose_name="문제 설명")

    def __str__(self):
        return f"question_{self.id}: {self.text[:30]}"

    class Meta:
        db_table = "question"
        verbose_name = "문제"
        verbose_name_plural = "문제"


class Choice(TimeStampedMixin):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choice"
    )
    text = models.TextField(
        null=False,
        blank=False,
    )
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"choice_{self.id}: {self.text[:30]}"

    class Meta:
        db_table = "question_choice"
        verbose_name = "선택지"
        verbose_name_plural = "선택지"
