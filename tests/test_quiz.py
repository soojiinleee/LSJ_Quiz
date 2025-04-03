import pytest

from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestManageQuiz:
    def test_create_quize_by_staff(self, api_client, staff_user_data):
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