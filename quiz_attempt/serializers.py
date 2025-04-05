from rest_framework import serializers

from django.shortcuts import get_object_or_404
from quiz.models import Quiz
from question.models import Question
from .models import QuizAttempt, QuizAttemptQuestion


class QuizAttemptCreateSerializer(serializers.ModelSerializer):
    quiz_id = serializers.IntegerField()
    question_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz_id', 'user_id', 'attempt_code', 'question_ids', 'attempt_question_count']
        read_only_fields = ['id', 'user_id', 'attempt_code', 'attempt_question_count']

    def validate(self, attrs):
        quiz_id = attrs.get('quiz_id')
        user = self.context['request'].user

        if QuizAttempt.objects.filter(user=user, quiz_id=quiz_id).exists():
            raise serializers.ValidationError("이미 응시한 퀴즈입니다.")  # TODO response 수정 {'non_field_errors': ['이미 응시한 퀴즈입니다.']}

        return attrs

    def create(self, validated_data):
        quiz_id = validated_data.pop('quiz_id')
        question_ids = validated_data.pop('question_ids')
        user = self.context['request'].user

        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions = Question.objects.filter(id__in=question_ids)

        # 응시 객체 생성
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            user=user,
            attempt_question_count=quiz.question_count
        )

        # 출제된 문제 저장 (순서 보존)
        for idx, question in enumerate(questions):
            QuizAttemptQuestion.objects.create(
                attempt=attempt,
                question=question,
                order_index=idx + 1
            )

        return attempt
