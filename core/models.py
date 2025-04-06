from django.db import models


class TimeStampedMixin(models.Model):
    """생성/수정 시간을 저장하는 Mixin"""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")

    class Meta:
        abstract = True
