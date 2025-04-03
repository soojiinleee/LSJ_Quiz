import pytest
from rest_framework.test import APIClient

from .factories import UserFactory, QuizFactory


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def staff_user_data():
    staff1 = UserFactory.create(username="staff1", email="staff1@staff.com",password="staff1", is_staff=True)

    return {"staff1": staff1}

@pytest.fixture
def user_data():
    user1 = UserFactory.create(username="user1", email="user1@user.com", password="user1", is_staff=False)

    return {"user1": user1}
