import factory
import faker

from django.contrib.auth.models import User

from question.models import Question, Choice
from quiz.models import Quiz, QuizQuestion
from quiz_attempt.models import QuizAttempt, QuizAttemptQuestion, QuizAttemptChoice

fake = faker.Faker("ko_KR")


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker("name")
    email = factory.Faker("email")
    password = factory.Faker("password")
    is_staff = False

    class Meta:
        model = User


class QuizFactory(factory.django.DjangoModelFactory):
    """퀴즈 Factory"""

    creator = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence")
    is_random_question = False
    is_random_choice = False
    question_count = factory.Faker("random_int")

    class Meta:
        model = Quiz


class QuestionFactory(factory.django.DjangoModelFactory):
    """문제 Factory"""
    text = factory.Faker('sentence')

    class Meta:
        model = Question


class ChoiceFactory(factory.django.DjangoModelFactory):
    """문제-선택지 Factory"""
    question = factory.SubFactory(QuestionFactory)
    text = factory.Faker('word')
    is_correct = False

    class Meta:
        model = Choice


class QuizQuestionFactory(factory.django.DjangoModelFactory):
    """퀴즈-문제 연결 Factory"""
    quiz = factory.SubFactory(QuizFactory)
    question = factory.SubFactory(QuestionFactory)

    class Meta:
        model = QuizQuestion


class QuizAttemptFactory(factory.django.DjangoModelFactory):
    """응시한 퀴즈 Factory"""
    quiz = factory.SubFactory(QuizFactory)
    user = factory.SubFactory(UserFactory)
    attempt_question_count= factory.Faker('random_int')
    started_at = factory.Faker('date_time')
    submitted_at = factory.Faker('date_time')

    class Meta:
        model = QuizAttempt


class QuizAttemptQuestionFactory(factory.django.DjangoModelFactory):
    """퀴즈 출제 문제"""
    attempt = factory.SubFactory(QuizAttemptFactory)
    question = factory.SubFactory(QuestionFactory)
    order_index = factory.Faker('random_int')

    class Meta:
        model = QuizAttemptQuestion


class QuizAttemptChoiceFactory(factory.django.DjangoModelFactory):
    """퀴즈 출제 문제 선택지"""

    attempt_question = factory.SubFactory(QuizAttemptQuestionFactory)
    choice = factory.SubFactory(ChoiceFactory)
    order_index = factory.Faker('random_int')
    is_selected = False

    class Meta:
        model = QuizAttemptChoice