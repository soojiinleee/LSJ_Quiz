import pytest

from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from question.models import Choice
from quiz_attempt.models import QuizAttempt, QuizAttemptChoice


@pytest.mark.django_db
class TestQuizAttempt:
    def test_quiz_attempt_create(self, api_client, user_data, quiz_data, question_data, quiz_question_data):
        """"퀴즈 응시 및 출제 문제 저장 테스트"""

        # given : 일반 유저 토큰 세팅
        user = User.objects.get(username='user1')
        api_client.force_authenticate(user=user)

        # given : request.data 세팅 (퀴즈 및 문제 데이터)
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

        # given : request.data 세팅 (퀴즈 및 문제 데이터)
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


@pytest.mark.django_db
class TestQuizAttemptQuestion:
    def test_quiz_attempt_question_detail(self, api_client, user_data,
                                          quiz_data, question_data, choice_data,
                                          quiz_attempt_data, quiz_attempt_question_data):
        """응시한 퀴즈 출제 문제 상세 조회 테스트 : 문제 & 선택지 확인"""

        # given : 일반 유저 토큰 세팅
        user = User.objects.get(username='user2')
        api_client.force_authenticate(user=user)

        # given : query params 세팅
        quiz_id = quiz_data['quiz3'].id
        question_id = quiz_attempt_question_data['attempt1_question2'].question.id

        # when : 출제 문제 상세 조회 API 호출
        url = reverse('quiz-attempt-question', kwargs={'question_id': question_id})
        response = api_client.get(url, {"quiz_id": quiz_id})

        # then : 문제 및 선택지 정보 확인
        response_data = response.json()
        question_obj = quiz_attempt_question_data['attempt1_question2'].question
        expected_choices = Choice.objects.filter(question=question_obj)
        expected_choice_texts = set(expected_choices.values_list('text', flat=True))
        actual_choice_texts = set(choice['text'] for choice in response_data['choices'])

        # then : 문제 확인
        assert response.status_code == status.HTTP_200_OK
        assert response_data['id'] == question_obj.id
        assert response_data['text'] == question_obj.text

        # then : 선택지 확인
        assert len(response_data['choices']) == expected_choices.count()
        assert actual_choice_texts == expected_choice_texts


# TODO 수정 필요
# @pytest.mark.django_db
# class TestQuizAttemptChoice:
#     def test_save_quiz_attempt_choice_order(self, api_client, user_data,
#                                             quiz_data, question_data, choice_data,
#                                             quiz_attempt_data, quiz_attempt_question_data,
#                                             quiz_attempt_choice_data):
#         """응시한 퀴즈 문제 선택지 배치 저장"""
#         # given : 일반 유저 토큰 세팅
#         user = User.objects.get(username='user2')
#         api_client.force_authenticate(user=user)
#
#         # given : request data 세팅
#         quiz_id = quiz_data['quiz3'].id
#         question_id = quiz_attempt_question_data['attempt1_question1'].question.id
#         choices = [
#             {
#                 "id": choice_data['choice3'].id,
#                 "order_index": 1,
#             },
#             {
#                 "id": choice_data['choice1'].id,
#                 "order_index": 2,
#             },
#             {
#                 "id": choice_data['choice2'].id,
#                 "order_index": 3,
#             }
#         ]
#         request_data = {
#             'quiz_id': quiz_id,
#             'question_id': question_id,
#             'choices': choices
#         }
#
#         # when: 응시한 퀴즈 문제 선택지 저장 API 호출
#         url = reverse('attempt-choice')
#         response = api_client.post(url, data=request_data, format='json')
#
#         # then : 선택지 저장 성공 확인
#         response_data = response.json()
#         stored = QuizAttemptChoice.objects.filter(attempt_question=quiz_attempt_question_data["attempt1_question1"])
#         print(stored)
#
#         assert response.status_code == status.HTTP_201_CREATED
#         assert stored.choice_id == choice_data["choice4"].id
#         assert stored.order_index == 1
#         assert stored.is_selected is False