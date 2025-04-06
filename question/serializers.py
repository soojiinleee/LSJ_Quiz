import random

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from quiz_attempt.models import QuizAttempt, QuizAttemptChoice
from .models import Question, Choice


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text", "is_correct"]
        extra_kwargs = {"is_correct": {"write_only": True}}


class QuestionSerializer(serializers.ModelSerializer):
    choice = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "text", "choice"]

    def validate_choice(self, value):
        correct_count = sum([1 for c in value if c.get("is_correct")])
        if correct_count != 1:
            raise serializers.ValidationError("정답은 반드시 1개만 있어야 합니다.")
        return value

    def create(self, validated_data):
        choices_data = validated_data.pop("choice")
        question = Question.objects.create(**validated_data)
        for choice_data in choices_data:
            Choice.objects.create(question=question, **choice_data)
        return question


class QuestionSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "text"]


class QuestionDetailWithChoicesSerializer(QuestionSimpleSerializer):
    choices = serializers.SerializerMethodField()
    is_ordered = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = QuestionSimpleSerializer.Meta.fields + ["choices", "is_ordered"]

    def _find_attempt_choices(self) -> (QuizAttemptChoice, QuizAttempt):
        user = self.context["request"].user
        quiz_id = self.context["request"].query_params.get("quiz_id")
        question_id = self.context["view"].kwargs.get("question_id")

        quiz_attempt = QuizAttempt.objects.get(quiz_id=quiz_id, user=user)
        attempt_question = quiz_attempt.questions.get(question_id=question_id)
        attempt_choices = attempt_question.choices.all()

        return attempt_choices, quiz_attempt

    @extend_schema_field(ChoiceSerializer(many=True))
    def get_choices(self, obj: Question):
        attempt_choices, quiz_attempt = self._find_attempt_choices()

        # 이전에 문제 조회하여 저장된 선택지 순서가 있는 경우
        if attempt_choices:
            ordered_choices = [
                attempt_choice.choice for attempt_choice in attempt_choices
            ]
            return ChoiceSerializer(ordered_choices, many=True).data

        # 처음 문제 조회 하는 경우
        choices = obj.choice.all()
        is_random_choice = quiz_attempt.quiz.is_random_choice

        if is_random_choice:
            choices = list(choices)
            random.shuffle(choices)

        return ChoiceSerializer(choices, many=True).data

    @extend_schema_field(serializers.BooleanField())
    def get_is_ordered(self, obj: Question):
        attempt_choices, _ = self._find_attempt_choices()
        return attempt_choices.exists()
