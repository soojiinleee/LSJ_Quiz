import pytest

from django.utils import timezone
from rest_framework.test import APIClient

from .factories import (
    UserFactory,
    QuizFactory,
    QuestionFactory,
    ChoiceFactory,
    QuizQuestionFactory,
    QuizAttemptFactory,
    QuizAttemptQuestionFactory,
    QuizAttemptChoiceFactory,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def staff_user_data():
    """관리자"""
    staff1 = UserFactory.create(
        username="staff1", email="staff1@staff.com", password="staff1", is_staff=True
    )

    return {"staff1": staff1}


@pytest.fixture
def user_data():
    """일반 유저"""
    user1 = UserFactory.create(
        username="user1", email="user1@user.com", password="user1", is_staff=False
    )
    user2 = UserFactory.create(
        username="user2", email="user2@user.com", password="user2", is_staff=False
    )

    return {"user1": user1, "user2": user2}


@pytest.fixture
def quiz_data(db, staff_user_data):
    quiz1 = QuizFactory.create(
        creator=staff_user_data["staff1"], title="퀴즈1", deleted_at=None
    )
    quiz2 = QuizFactory.create(
        creator=staff_user_data["staff1"],
        title="퀴즈2",
        is_random_question=True,
        is_random_choice=True,
        deleted_at=None,
    )
    quiz3 = QuizFactory.create(
        creator=staff_user_data["staff1"],
        title="퀴즈3",
        question_count=3,
        is_random_question=True,
        is_random_choice=True,
        deleted_at=None,
    )
    return {"quiz1": quiz1, "quiz2": quiz2, "quiz3": quiz3}


@pytest.fixture
def quiz_pagination_data(db):
    """퀴즈 목록 페이지네이션 테스트"""
    return QuizFactory.create_batch(120)


@pytest.fixture
def question_data(db):
    question1 = QuestionFactory.create(text="다음 중 설명이 맞는 것은?")
    question2 = QuestionFactory.create(text="다음 중 설명이 틀린 것은?")
    question3 = QuestionFactory.create(text="지문에서 확인 할 수 없는 것은?")
    return {"question1": question1, "question2": question2, "question3": question3}


@pytest.fixture
def choice_data(db, question_data):
    choice1 = ChoiceFactory.create(
        question=question_data["question1"], text="문제1의 선택지1", is_correct=True
    )
    choice2 = ChoiceFactory.create(
        question=question_data["question1"], text="문제1의 선택지2"
    )
    choice3 = ChoiceFactory.create(
        question=question_data["question1"], text="문제1의 선택지3"
    )
    choice4 = ChoiceFactory.create(
        question=question_data["question2"], text="문제2의 선택지1"
    )
    choice5 = ChoiceFactory.create(
        question=question_data["question2"], text="문제2의 선택지2", is_correct=True
    )
    choice6 = ChoiceFactory.create(
        question=question_data["question3"], text="문제3의 선택지1"
    )
    choice7 = ChoiceFactory.create(
        question=question_data["question3"], text="문제3의 선택지2"
    )
    choice8 = ChoiceFactory.create(
        question=question_data["question3"], text="문제3의 선택지3"
    )
    choice9 = ChoiceFactory.create(
        question=question_data["question3"], text="문제3의 선택지4"
    )
    return {
        "choice1": choice1,
        "choice2": choice2,
        "choice3": choice3,
        "choice4": choice4,
        "choice5": choice5,
        "choice6": choice6,
        "choice7": choice7,
        "choice8": choice8,
        "choice9": choice9,
    }


@pytest.fixture
def quiz_question_data(db, quiz_data, question_data):
    quiz1_question1 = QuizQuestionFactory.create(
        quiz=quiz_data["quiz1"],
        question=question_data["question1"],
    )
    quiz1_question2 = QuizQuestionFactory.create(
        quiz=quiz_data["quiz1"],
        question=question_data["question2"],
    )
    quiz3_question1 = QuizQuestionFactory.create(
        quiz=quiz_data["quiz3"],
        question=question_data["question1"],
    )
    quiz3_question2 = QuizQuestionFactory.create(
        quiz=quiz_data["quiz3"],
        question=question_data["question2"],
    )
    quiz3_question3 = QuizQuestionFactory.create(
        quiz=quiz_data["quiz3"],
        question=question_data["question3"],
    )

    return {
        "quiz1_question1": quiz1_question1,
        "quiz1_question2": quiz1_question2,
        "quiz3_question1": quiz3_question1,
        "quiz3_question2": quiz3_question2,
        "quiz3_question3": quiz3_question3,
    }


@pytest.fixture
def quiz_with_questions_batch_data(db):
    """퀴즈 출제 문제 랜덤 배치 X"""
    quiz = QuizFactory(question_count=30, is_random_question=False)
    questions = QuestionFactory.create_batch(50)

    for q in questions:
        QuizQuestionFactory(quiz=quiz, question=q)

    return quiz


@pytest.fixture()
def quiz_attempt_data(db, user_data, quiz_data):
    attempt1 = QuizAttemptFactory.create(
        user=user_data["user2"],
        quiz=quiz_data["quiz3"],
        attempt_question_count=quiz_data["quiz3"].question_count,
        started_at=timezone.now(),
        submitted_at=None,
    )

    return {"attempt1": attempt1}


@pytest.fixture()
def quiz_attempt_question_data(db, quiz_attempt_data, question_data):
    attempt1_question2 = QuizAttemptQuestionFactory.create(
        attempt=quiz_attempt_data["attempt1"],
        question=question_data["question2"],
        order_index=1,
    )
    attempt1_question1 = QuizAttemptQuestionFactory.create(
        attempt=quiz_attempt_data["attempt1"],
        question=question_data["question1"],
        order_index=2,
    )
    attempt1_question3 = QuizAttemptQuestionFactory.create(
        attempt=quiz_attempt_data["attempt1"],
        question=question_data["question3"],
        order_index=3,
    )

    return {
        "attempt1_question2": attempt1_question2,
        "attempt1_question1": attempt1_question1,
        "attempt1_question3": attempt1_question3,
    }


@pytest.fixture()
def quiz_attempt_choice_data(db, quiz_attempt_question_data, choice_data):
    # 선택지 저장 및 선택지 고른 상태
    attempt1_choice1 = QuizAttemptChoiceFactory.create(
        attempt_question=quiz_attempt_question_data["attempt1_question2"],
        choice=choice_data["choice5"],
        order_index=1,
        is_selected=True,  # 정답 맞춤
    )
    attempt1_choice2 = QuizAttemptChoiceFactory.create(
        attempt_question=quiz_attempt_question_data["attempt1_question2"],
        choice=choice_data["choice4"],
        order_index=2,
    )
    # 선택지 저장만 한 상태
    attempt1_choice3 = QuizAttemptChoiceFactory.create(
        attempt_question=quiz_attempt_question_data["attempt1_question1"],
        choice=choice_data["choice3"],
        order_index=1,
    )
    attempt1_choice4 = QuizAttemptChoiceFactory.create(
        attempt_question=quiz_attempt_question_data["attempt1_question1"],
        choice=choice_data["choice1"],
        order_index=2,
    )
    attempt1_choice5 = QuizAttemptChoiceFactory.create(
        attempt_question=quiz_attempt_question_data["attempt1_question1"],
        choice=choice_data["choice2"],
        order_index=3,
    )
    return {
        "attempt1_choice1": attempt1_choice1,
        "attempt1_choice2": attempt1_choice2,
        "attempt1_choice3": attempt1_choice3,
        "attempt1_choice4": attempt1_choice4,
        "attempt1_choice5": attempt1_choice5,
    }
