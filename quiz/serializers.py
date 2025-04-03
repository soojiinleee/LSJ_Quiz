from rest_framework import serializers
from .models import Quiz, QuizQuestion
from question.models import Question


class QuizCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'is_random_question', 'is_random_choice']
        read_only_fields = ['id']

    def create(self, validated_data):
        request = self.context['request']
        validated_data['created_by'] = request.user
        return super().create(validated_data)


class QuizQuestionLinkSerializer(serializers.Serializer):
    question_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        write_only=True
    )

    def validate_question_ids(self, value):
        questions = Question.objects.filter(id__in=value)
        if questions.count() != len(set(value)):
            raise serializers.ValidationError("존재하지 않는 문제 ID가 포함되어 있습니다.")
        return value

    def create(self, validated_data):
        quiz_id = self.context['quiz_id']
        quiz = Quiz.objects.get(pk=quiz_id)

        question_ids = validated_data['question_ids']
        questions = Question.objects.filter(id__in=question_ids)

        linked_questions = []

        for question in questions:
            obj, created = QuizQuestion.objects.get_or_create(quiz=quiz, question=question)

            if not created:
                raise serializers.ValidationError("이미 퀴즈와 연결된 문제입니다.")

            if created:
                linked_questions.append(question.id)

        return {"quiz_id": quiz.id, "linked_questions": linked_questions}
