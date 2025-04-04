from rest_framework import serializers
from .models import Question, Choice


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'code', 'text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    choice = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'code', 'text', 'choice']

    def validate_choice(self, value):
        correct_count = sum([1 for c in value if c.get('is_correct')])
        if correct_count != 1:
            raise serializers.ValidationError("정답은 반드시 1개만 있어야 합니다.")
        return value

    def create(self, validated_data):
        choices_data = validated_data.pop('choice')
        question = Question.objects.create(**validated_data)
        for choice_data in choices_data:
            Choice.objects.create(question=question, **choice_data)
        return question


class QuestionSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'code', 'text']
