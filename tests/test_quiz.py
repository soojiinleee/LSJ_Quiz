import pytest

from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestManageQuiz:
    def test_create_quiz_by_staff(self, api_client, staff_user_data):
        """관리자 퀴즈 생성 테스트"""

        # given : 관리자 토큰 세팅
        staff = User.objects.get(username='staff1')
        api_client.force_authenticate(user=staff)

        # when : 퀴즈 생성 API 호출
        url = reverse('quiz-manage-list')
        request_data = {"title": "test_quiz"}
        response = api_client.post(url, data=request_data)

        # then : 퀴즈 생성 확인
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()['title'] == 'test_quiz'
        assert response.json()['is_random_question'] == False
        assert response.json()['is_random_choice'] == False

    def test_create_quiz_by_user(self, api_client, user_data):
        """일반 유저 퀴즈 생성 테스트"""

        # given : 일반 유저 토큰 세팅
        user = User.objects.get(username='user1')
        api_client.force_authenticate(user=user)

        # when : 퀴즈 생성 API 호출
        url = reverse('quiz-manage-list')
        request_data = {"title": "test_quiz"}
        response = api_client.post(url, data=request_data)

        # then : 퀴즈 생성 실패
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "권한이 없습니다."


@pytest.mark.django_db
class TestQuizQuestionLink:
    def test_link_to_quiz_question(self, api_client, quiz_data, question_data):
        """퀴즈-문제 연결 테스트"""

        # given : 관리자 토큰 세팅
        staff = User.objects.get(username='staff1')
        api_client.force_authenticate(user=staff)

        # when : 퀴즈, 문제 데이터
        quiz_id = quiz_data['quiz2'].id
        question_id=question_data["question3"].id
        request_data = {"question_ids": [question_id]}

        # when : 퀴즈-문제 연결 API 호출
        url = reverse('quiz-question-link', kwargs={'quiz_id': quiz_id})
        response = api_client.post(url, data=request_data)

        # then : 퀴즈-문제 연결 성공
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["quiz_id"] == quiz_id
        assert question_data["question3"].id in response.json()["linked_questions"]

    def test_already_linked_to_quiz_question(self, api_client, quiz_question_data):
        """퀴즈-문제 중복 연결 테스트"""

        # given : 관리자 토큰 세팅
        staff = User.objects.get(username='staff1')
        api_client.force_authenticate(user=staff)

        # when : 퀴즈, 문제 데이터
        quiz_id = quiz_question_data['quiz1_question1'].quiz.id
        question_id = quiz_question_data['quiz1_question1'].question.id
        request_data = {"question_ids": [question_id]}

        # when : 퀴즈-문제 연결 API 호출
        url = reverse('quiz-question-link', kwargs={'quiz_id': quiz_id})
        response = api_client.post(url, data=request_data)

        # then : 퀴즈-문제 연결 실패
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()[0] == "이미 퀴즈와 연결된 문제입니다."

    def test_link_to_quiz_with_not_existed_question(self, api_client, quiz_data, question_data):
        """퀴즈-문제 연결 테스트 : 문제 id 오류"""

        # given : 관리자 토큰 세팅
        staff = User.objects.get(username='staff1')
        api_client.force_authenticate(user=staff)

        # when : 퀴즈, 문제 데이터
        quiz_id = quiz_data['quiz2'].id
        question_id = (question_data["question3"].id + 100)
        request_data = {"question_ids": [question_id]}

        # when : 퀴즈-문제 연결 API 호출
        url = reverse('quiz-question-link', kwargs={'quiz_id': quiz_id})
        response = api_client.post(url, data=request_data)

        # then : 문제 오류 에러 발생
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["question_ids"][0] == '존재하지 않는 문제 ID가 포함되어 있습니다.'