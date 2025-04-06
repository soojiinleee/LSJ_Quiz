from datetime import datetime
from rest_framework import serializers

from question.models import Question
from quiz_attempt.models import QuizAttempt
from .models import Quiz, QuizQuestion


class QuizIdTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ["id", "title"]
        read_only_fields = ["id"]


class BaseQuizSerializer(QuizIdTitleSerializer):
    class Meta(QuizIdTitleSerializer.Meta):
        fields = QuizIdTitleSerializer.Meta.fields + [
            "question_count",
            "is_random_question",
            "is_random_choice",
        ]


class QuizCreateUpdateSerializer(BaseQuizSerializer):
    def validate_question_count(self, value):
        if self.instance:
            related_question_count = self.instance.related_questions.count()
            if value > related_question_count:
                raise serializers.ValidationError(
                    f"문제 수는 현재 연결된 문제 수({related_question_count} 개)를 초과할 수 없습니다."
                )
        return value

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["creator"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 변경 사항이 없는 경우: 저장 생략, 그대로 반환
        changed = False
        for attr, value in validated_data.items():
            if getattr(instance, attr) != value:
                setattr(instance, attr, value)
                changed = True
        if changed:
            instance.save()
        return instance


class QuizStaffListSerializer(QuizIdTitleSerializer):
    pass


class QuizStaffDetailSerializer(BaseQuizSerializer):
    pass


class QuizUserSerializer(QuizIdTitleSerializer):
    has_attempted = serializers.SerializerMethodField()

    class Meta(QuizIdTitleSerializer.Meta):
        fields = QuizIdTitleSerializer.Meta.fields + ["has_attempted"]

    def get_has_attempted(self, obj):
        user = self.context["request"].user
        return QuizAttempt.objects.filter(quiz=obj, user=user).exists()


class QuizQuestionLinkSerializer(serializers.Serializer):
    question_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False, write_only=True
    )

    def validate_question_ids(self, value):
        questions = Question.objects.filter(id__in=value)
        if questions.count() != len(set(value)):
            raise serializers.ValidationError(
                "존재하지 않는 문제 ID가 포함되어 있습니다."
            )
        return value

    def create(self, validated_data):
        quiz_id = self.context["quiz_id"]
        quiz = Quiz.objects.get(pk=quiz_id)

        question_ids = validated_data["question_ids"]
        questions = Question.objects.filter(id__in=question_ids)

        linked_questions = []

        for question in questions:
            obj, created = QuizQuestion.objects.get_or_create(
                quiz=quiz, question=question
            )

            if not created:
                raise serializers.ValidationError("이미 퀴즈와 연결된 문제입니다.")

            if created:
                linked_questions.append(question.id)

        return {"quiz_id": quiz.id, "linked_questions": linked_questions}
