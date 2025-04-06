from rest_framework import serializers

from django.utils import timezone
from django.shortcuts import get_object_or_404
from quiz.models import Quiz
from question.models import Question, Choice
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
            raise serializers.ValidationError("이미 응시한 퀴즈입니다.")

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
    choice_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)


    def validate(self, attrs):
        question_id = attrs['question_id']
        choice_ids = attrs['choice_ids']

        # 문제에 포함된 선택지 여부 확인
        valid_ids = list(Choice.objects.filter(question_id=question_id).values_list('id', flat=True))
        invalid_ids = set(choice_ids) - set(valid_ids)
        if invalid_ids:
            raise serializers.ValidationError(f"유효하지 않은 choice id: {invalid_ids}")

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        quiz_id = validated_data.pop('quiz_id')
        question_id = validated_data.pop('question_id')
        choice_ids = validated_data.pop('choice_ids')

        quiz_attempt = get_object_or_404(QuizAttempt, user=user, quiz_id=quiz_id)
        attempt_question = quiz_attempt.questions.get(question_id=question_id)

        quiz_attempt_choice = QuizAttemptChoice.objects.filter(attempt_question=attempt_question)
        if quiz_attempt_choice:
            return quiz_attempt_choice

        # 선택지 순서 저장
        saved_choice=[
            QuizAttemptChoice(
                attempt_question=attempt_question,
                choice_id=choice_id,
                order_index=idx + 1
            )
            for idx, choice_id in enumerate(choice_ids)
        ]

        return QuizAttemptChoice.objects.bulk_create(saved_choice)


class QuizAttemptChoiceUpdateSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField(write_only=True)
    question_id = serializers.IntegerField(write_only=True)
    selected_choice_id = serializers.IntegerField(write_only=True)

    def update(self, instance, validated_data):
        instance.is_selected = True
        instance.save()
        return instance


class QuizSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = ['id', 'correct_count', 'submitted_at']
        read_only_fields = ['id', 'correct_count', 'submitted_at']

    def update(self, instance: QuizAttempt, validated_data):
        if instance.submitted_at:
            raise serializers.ValidationError("이미 제출된 퀴즈입니다.")

        correct_count = 0
        for attempt_question in instance.questions.all():
            # 선택된 선택지를 가져옴
            selected_choice = attempt_question.choices.filter(is_selected=True).first()

            if selected_choice:
                # 정답 여부 판별
                is_correct = selected_choice and selected_choice.choice.is_correct
                attempt_question.is_correct = is_correct
                attempt_question.save()

                if is_correct:
                    correct_count += 1

        # 정답 개수, 제출 시간 기록
        instance.correct_count = correct_count
        instance.submitted_at = timezone.now()
        instance.save()

        return instance