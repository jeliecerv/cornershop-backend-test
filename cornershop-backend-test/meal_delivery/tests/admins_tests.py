import pytest
from django.urls import reverse

from factory.faker import faker

from meal_delivery.tests.fixtures import *

from ..models import User


@pytest.mark.django_db
def test_user_admin_create():
    User.objects.create_user(
        first_name="John",
        last_name="Lennon",
        username="jhon.lennon",
        email="lennon@thebeatles.com",
        password="AbbeyRoad1969",
        user_type=User.ADMIN,
    )
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_auth_view(auto_login_user_admin):
    client, user = auto_login_user_admin()
    url = reverse("login")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_menu_list_view(auto_login_user_admin):
    client, user = auto_login_user_admin()
    url = reverse("admins:menu_list")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_menu_list_with_employee_view(auto_login_user_employee):
    client, user = auto_login_user_employee()
    url = reverse("admins:menu_list")
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_menu_list_view(auto_login_user_admin):
    client, user = auto_login_user_admin()
    url = reverse("admins:menu_add")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_menu_list_post_view(auto_login_user_admin):
    client, user = auto_login_user_admin()
    url = reverse("admins:menu_add")
    fake = faker.Faker()
    data = {
        "name": fake.name(),
        "date": fake.date(),
        "additional_text": fake.text(max_nb_chars=20),
        "items-0-order": fake.random_int(),
        "items-0-description": fake.text(max_nb_chars=20),
        "items-0-salad": True,
        "items-0-dessert": True,
        "items-TOTAL_FORMS": 1,
        "items-INITIAL_FORMS": 0,
        "items-MIN_NUM_FORMS": 0,
        "items-MAX_NUM_FORMS": 100,
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse("admins:menu_list")


@pytest.mark.django_db
def test_menu_edit_view(auto_login_user_admin, menu_factory):
    client, user = auto_login_user_admin()
    menu = menu_factory()
    url = reverse("admins:menu_change", kwargs={"pk": menu.pk})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_menu_edit_post_view(auto_login_user_admin, menu_factory):
    client, user = auto_login_user_admin()
    menu = menu_factory()
    url = reverse("admins:menu_change", kwargs={"pk": menu.pk})
    fake = faker.Faker()
    data = {
        "name": fake.name(),
        "date": fake.date(),
        "additional_text": fake.text(max_nb_chars=20),
        "items-0-order": fake.random_int(),
        "items-0-description": fake.text(max_nb_chars=20),
        "items-0-salad": True,
        "items-0-dessert": True,
        "items-TOTAL_FORMS": 1,
        "items-INITIAL_FORMS": 0,
        "items-MIN_NUM_FORMS": 0,
        "items-MAX_NUM_FORMS": 100,
    }
    response = client.put(url)
    assert menu.name != data["name"]
    assert response.status_code == 200


@pytest.mark.django_db
def test_send_menu_slack(mocker, menu_factory):
    client_mock = mocker.patch(
        "slack.WebClient.chat_postMessage",
        return_value={"message": {"text": "test message"}},
    )
    menu = menu_factory()
    menu.send_menu_slack(client_mock)
    assert len(client_mock.method_calls) == 1
