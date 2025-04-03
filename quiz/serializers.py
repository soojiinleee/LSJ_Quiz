from rest_framework import serializers
from .models import Quiz


class QuizCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'is_random_question', 'is_random_choice']
        read_only_fields = ['id']

    def create(self, validated_data):
        request = self.context['request']
        validated_data['created_by'] = request.user
        return super().create(validated_data)