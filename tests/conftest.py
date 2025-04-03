import pytest
from rest_framework.test import APIClient

from .factories import UserFactory, QuizFactory, QuestionFactory, ChoiceFactory, QuizQuestionFactory


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def staff_user_data():
    """관리자"""
    staff1 = UserFactory.create(username="staff1", email="staff1@staff.com",password="staff1", is_staff=True)

    return {"staff1": staff1}

@pytest.fixture
def user_data():
    """일반 유저"""
    user1 = UserFactory.create(username="user1", email="user1@user.com", password="user1", is_staff=False)

    return {"user1": user1}

@pytest.fixture
def quiz_data(db, staff_user_data):
    quiz1 = QuizFactory.create(
        created_by=staff_user_data["staff1"],
        title="퀴즈1",
    )
    quiz2 = QuizFactory.create(
        created_by=staff_user_data["staff1"],
        title="퀴즈2",
        is_random_question=True,
        is_random_choice=True
    )
    return {"quiz1": quiz1, "quiz2": quiz2}

@pytest.fixture
def question_data(db):
    question1 = QuestionFactory.create(
        text="다음 중 설명이 맞는 것은?"
    )
    question2 = QuestionFactory.create(
        text="다음 중 설명이 틀린 것은?"
    )
    question3 = QuestionFactory.create(
        text="지문에서 확인 할 수 없는 것은?"
    )
    return {"question1": question1, "question2": question2, "question3": question3}

@pytest.fixture
def choice_data(db, question_data):
    choice1 = ChoiceFactory.create(
        question=question_data["question1"],
        text="문제1의 선택지1",
        is_correct=True
    )
    choice2 = ChoiceFactory.create(
        question=question_data["question1"],
        text="문제1의 선택지2"
    )
    choice3 = ChoiceFactory.create(
        question=question_data["question1"],
        text="문제1의 선택지3"
    )
    choice4 = ChoiceFactory.create(
        question=question_data["question2"],
        text="문제2의 선택지1"
    )
    choice5 = ChoiceFactory.create(
        question=question_data["question2"],
        text="문제2의 선택지2",
        is_correct=True
    )
    choice6 = ChoiceFactory.create(
        question=question_data["question3"],
        text="문제3의 선택지1"
    )
    choice7 = ChoiceFactory.create(
        question=question_data["question3"],
        text="문제3의 선택지2"
    )
    choice8 = ChoiceFactory.create(
        question=question_data["question3"],
        text="문제3의 선택지3"
    )
    choice9 = ChoiceFactory.create(
        question=question_data["question3"],
        text="문제3의 선택지4"
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

    return {
        "quiz1_question1": quiz1_question1,
        "quiz1_question2": quiz1_question2
    }