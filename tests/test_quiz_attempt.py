import pytest

from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from quiz_attempt.models import QuizAttempt


@pytest.mark.django_db
class TestQuizAttempt:
    def test_quiz_attempt_create(self, api_client, user_data, quiz_data, question_data, quiz_question_data):
        """"퀴즈 응시 및 출제 문제 저장 테스트"""

        # given : 일반 유저 토큰 세팅
        user = User.objects.get(username='user1')
        api_client.force_authenticate(user=user)

        # when : request.data 세팅 (퀴즈 및 문제 데이터)
        quiz_id = quiz_data['quiz3'].id
        question_ids = [question_data['question2'].id, question_data['question3'].id, question_data['question1'].id]
        request_data = {
            'quiz_id': quiz_id,
            'question_ids': question_ids,
        }

        # when : 퀴즈 응시 API 호출
        url = reverse('quiz-attempt')
        response = api_client.post(url, data=request_data)

        # then : 퀴즈 응시 내역 확인 (quiz_attempt)
        response_data = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        assert response_data["attempt_question_count"] == len(question_ids)

        # then : 퀴즈 출제 문제 순서 저장 확인 (quiz_attempt_question)
        attempt = QuizAttempt.objects.get(user=user, quiz_id=quiz_id)
        saved_questions = attempt.questions.all().order_by('order_index')
        sorted_saved_questions = sorted(saved_questions, key=lambda x: x.order_index)

        assert sorted_saved_questions[2].question_id == question_ids[1]

    def test_already_attempted_quiz(self, api_client, user_data, quiz_data, question_data, quiz_attempt_data):
        """응시 이력 있는 퀴즈 재응시 테스트"""

        # given : 일반 유저 토큰 세팅
        user = User.objects.get(username='user2')
        api_client.force_authenticate(user=user)

        # when : request.data 세팅 (퀴즈 및 문제 데이터)
        quiz_id = quiz_data['quiz3'].id
        question_ids = [question_data['question2'].id, question_data['question3'].id, question_data['question1'].id]
        request_data = {
            'quiz_id': quiz_id,
            'question_ids': question_ids,
        }

        # when : 퀴즈 응시 API 호출
        url = reverse('quiz-attempt')
        response = api_client.post(url, data=request_data)

        # then : 재응시 불가
        assert response.status_code == status.HTTP_400_BAD_REQUEST
