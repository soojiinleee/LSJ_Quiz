import pytest
from urllib.parse import urlparse
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestCreateUpdateQuiz:
    def test_create_quiz_by_staff(self, api_client, staff_user_data):
        """관리자 퀴즈 생성 테스트"""

        # given : 관리자 토큰 세팅
        staff = User.objects.get(username='staff1')
        api_client.force_authenticate(user=staff)

        # when : 퀴즈 생성 API 호출
        url = reverse('quiz-staff-list')
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
        url = reverse('quiz-staff-list')
        request_data = {"title": "test_quiz"}
        response = api_client.post(url, data=request_data)

        # then : 퀴즈 생성 실패
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "권한이 없습니다."

    def test_update_quiz_question_count(self, api_client, staff_user_data, quiz_data, quiz_question_data):
        """퀴즈 문제 개수 설정 (0 -> 2)"""

        # given : 관리자 토큰 세팅
        staff = User.objects.get(username='staff1')
        api_client.force_authenticate(user=staff)

        # when : 퀴즈 수정 API 호출
        url = reverse('quiz-staff-detail', kwargs={'pk': quiz_data['quiz1'].id})
        request_data = {"question_count": 2}
        response = api_client.patch(url, data=request_data)

        # then : 퀴즈에 출제할 문제 수 지정 성공
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["question_count"] == 2

    def test_fail_update_quiz_question_count(self, api_client, staff_user_data, quiz_data, quiz_question_data):
        """퀴즈 문제 개수 설정 불가 : 퀴즈에 연결된 문제 개수 초과"""

        # given : 관리자 토큰 세팅
        staff = User.objects.get(username='staff1')
        api_client.force_authenticate(user=staff)

        # when : 퀴즈 수정 API 호출
        url = reverse('quiz-staff-detail', kwargs={'pk': quiz_data['quiz2'].id})
        request_data = {"question_count": 2}
        response = api_client.patch(url, data=request_data)

        # then : 퀴즈에 출제할 문제 수 설정 실패
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["question_count"][0] == '문제 수는 현재 연결된 문제 수(0 개)를 초과할 수 없습니다.'

    def test_update_quiz_question_random_order(self, api_client, staff_user_data, quiz_data):
        """퀴즈 내 문제 및 선택지 순서 랜덤 정렬"""

        # given : 관리자 토큰 세팅
        staff = User.objects.get(username='staff1')
        api_client.force_authenticate(user=staff)

        # when : 퀴즈 수정 API 호출
        url = reverse('quiz-staff-detail', kwargs={'pk': quiz_data['quiz1'].id})
        request_data = {"is_random_question": True, "is_random_choice": True}
        response = api_client.patch(url, data=request_data)

        # then : 퀴즈에 출제할 문제 및 선택지 랜덤 정렬 설정 성공
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_random_question"] == True
        assert response.json()["is_random_choice"] == True


@pytest.mark.django_db
class TestQuizStaff:

    def test_quiz_list_by_staff(self, api_client, staff_user_data, quiz_pagination_data):
        """관리자 - 퀴즈 목록 조회 테스트"""

        # given : 관리자 토큰 세팅
        staff = User.objects.get(username='staff1')
        api_client.force_authenticate(user=staff)

        # when : 퀴즈-문제 연결 API 호출
        url = reverse('quiz-staff-list')
        response = api_client.get(url)

        # then : 퀴즈 전체 목록 조회
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['count'] == len(quiz_pagination_data)

    def test_quiz_list_pagination(self, api_client, staff_user_data, quiz_pagination_data):
        """관리자 - 퀴즈 목록 페이지네이션 테스트"""

        # given : 관리자 토큰 세팅
        staff = User.objects.get(username='staff1')
        api_client.force_authenticate(user=staff)

        # when : 퀴즈-문제 연결 API 호출
        url = reverse('quiz-staff-list')
        response = api_client.get(url, data={'page':3})

        # then : 이전 페이지, 다음 페이지 확인
        next_url = urlparse(response.json()['next'])
        next_page = f"{next_url.query}"
        previous_url = urlparse(response.json()['previous'])
        previous_page = f"{previous_url.query}"

        # then : 현재 페이지 퀴즈 목록 조회
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['count'] == len(quiz_pagination_data)
        assert next_page == "page=4"
        assert previous_page == "page=2"


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


@pytest.mark.django_db
class TestQuizQuestionList:

    def test_quiz_question_list(self, api_client, user_data, quiz_with_questions_batch_data):
        """퀴즈 출제 문제 목록 조회 및 페이지네이션 테스트"""

        # given : 일반 유저 토큰 세팅
        user = User.objects.get(username='user1')
        api_client.force_authenticate(user=user)

        # when : 퀴즈 출제 문제 목록 마지막 페이지 호출
        quiz_id = quiz_with_questions_batch_data.id
        url = reverse('quiz-question', kwargs={'quiz_id': quiz_id})
        response = api_client.get(url, data={'page':3})

        # then : 다음 페이지 확인
        previous_url = urlparse(response.json()['previous'])
        previous_page = f"{previous_url.query}"

        # then : 퀴즈 출제 목록 현재 페이지 개수 & 페이지네이션 확인
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == quiz_with_questions_batch_data.question_count
        assert previous_page == "page=2"

    # def test_quiz_question_random_order(self, api_client, user_data):
    #     # TODO 문제 랜덤 조회 확인 -> mock 데이터 생성 필요
    #
    #     # given : 일반 유저 토큰 세팅
    #     user = User.objects.get(username='user1')
    #     api_client.force_authenticate(user=user)
    #
    #     # when : 퀴즈 출제 문제 목록 호출
    #     quiz_id = quiz_with_questions_batch_data.id
    #     url = reverse('quiz-question', kwargs={'quiz_id': quiz_id})
    #     response = api_client.get(url)

