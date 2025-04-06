from rest_framework import serializers

from django.shortcuts import get_object_or_404
from quiz.models import Quiz
from question.models import Question
from .models import QuizAttempt, QuizAttemptQuestion, QuizAttemptChoice


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


class QuizAttemptChoiceCreateSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField(write_only=True)
    question_id = serializers.IntegerField(write_only=True)
    choices = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),
        allow_empty=False
    )

    # def validate(self, attrs):
    #     attempt_question = self.context['attempt_question']
    #     choice_ids = [item['id'] for item in attrs['choices']]
    #
    #     # 해당 문제에 포함된 선택지만 허용
    #     valid_ids = attempt_question.question.choice.values_list('id', flat=True)
    #     invalid_ids = set(choice_ids) - set(valid_ids)
    #     if invalid_ids:
    #         raise serializers.ValidationError(f"유효하지 않은 choice id: {invalid_ids}")
    #
    #     return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        quiz_id = validated_data.get('quiz_id', None)
        question_id = validated_data['question_id']
        choice_data = validated_data['choices']

        quiz_attempt = get_object_or_404(QuizAttempt, user=user, quiz_id=quiz_id)
        attempt_question = quiz_attempt.questions.select_related('question').get(question_id=question_id)
        quiz_attempt_choice = QuizAttemptChoice.objects.filter(attempt_question=attempt_question)

        if quiz_attempt_choice:
            return quiz_attempt_choice

        choices = [
            QuizAttemptChoice(
                attempt_question=attempt_question,
                choice_id=item['id'],
                order_index=item['order_index']
            ) for item in choice_data
        ]
        print(choices)

        return QuizAttemptChoice.objects.bulk_create(choices)


class QuizAttemptChoiceUpdateSerializer(serializers.Serializer):
    selected_choice_id = serializers.IntegerField()

    def validate_selected_choice_id(self, value):
        attempt_question = self.context['attempt_question']
        if not attempt_question.choices.filter(choice_id=value).exists():
            raise serializers.ValidationError("해당 선택지는 현재 문제에 포함되지 않습니다.")
        return value

    def save(self, **kwargs):
        attempt_question = self.context['attempt_question']
        selected_id = self.validated_data['selected_choice_id']

        # 모든 선택지 선택 해제
        QuizAttemptChoice.objects.filter(attempt_question=attempt_question).update(is_selected=False)

        # 선택된 선택지만 True
        QuizAttemptChoice.objects.filter(
            attempt_question=attempt_question, choice_id=selected_id
        ).update(is_selected=True)

        return {'selected_choice_id': selected_id}
