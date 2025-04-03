import factory
import faker

from django.contrib.auth.models import User
from quiz.models import Quiz


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

    created_by = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence")
    is_random_question = False
    is_random_choice = False

    class Meta:
        model = Quiz