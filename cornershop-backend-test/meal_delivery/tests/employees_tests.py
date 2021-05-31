import pytest
from factory.faker import faker
from django.urls import reverse

from meal_delivery.tests.fixtures import *

from ..models import User, Employee, Meal
import datetime


@pytest.mark.django_db
def test_user_employee_create():
    user = User.objects.create_user(
        first_name="John",
        last_name="Lennon",
        username="jhon.lennon",
        email="lennon@thebeatles.com",
        password="AbbeyRoad1969",
        user_type=User.ADMIN,
    )
    Employee.objects.create(user=user, phone="78965412")
    assert Employee.objects.count() == 1


@pytest.mark.django_db
def test_auth_employee_view(auto_login_user_employee):
    client, user = auto_login_user_employee()
    url = reverse("login")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_meal_history_list_view(auto_login_user_employee):
    client, user = auto_login_user_employee()
    url = reverse("employees:meal_history_list")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_meal_history_list_with_admin_view(auto_login_user_admin):
    client, user = auto_login_user_admin()
    url = reverse("employees:meal_history_list")
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_select_meal_view(auto_login_user_employee, menu_item_factory):
    client, user = auto_login_user_employee()
    menu_item_1 = menu_item_factory()
    menu_item_2 = menu_item_factory(menu=menu_item_1.menu)
    menu_item_3 = menu_item_factory(menu=menu_item_1.menu)
    url = reverse("employees:select_meal", kwargs={"pk": menu_item_1.menu.pk})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_select_meal_post_wrong_date_view(auto_login_user_employee, menu_item_factory):
    client, user = auto_login_user_employee()
    menu_item_1 = menu_item_factory()
    menu_item_2 = menu_item_factory(menu=menu_item_1.menu)
    menu_item_3 = menu_item_factory(menu=menu_item_1.menu)
    url = reverse("employees:select_meal", kwargs={"pk": menu_item_1.menu.pk})
    fake = faker.Faker()
    data = {
        "menu_item": menu_item_3.pk,
        "preference": fake.text(max_nb_chars=50),
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse(
        "employees:select_meal", kwargs={"pk": menu_item_1.menu.pk}
    )
    assert Meal.objects.filter(employee=user).count() == 0


@pytest.mark.django_db
def test_select_meal_post_right_date_view(
    monkeypatch,
    auto_login_user_employee,
    menu_factory,
    menu_item_factory,
):
    client, user = auto_login_user_employee()
    menu = menu_factory(date=datetime.date.today())
    menu_item_1 = menu_item_factory(menu=menu)
    menu_item_2 = menu_item_factory(menu=menu)
    menu_item_3 = menu_item_factory(menu=menu)
    url = reverse("employees:select_meal", kwargs={"pk": menu.pk})
    fake = faker.Faker()
    data = {
        "menu_item": menu_item_2.pk,
        "preference": fake.text(max_nb_chars=50),
    }
    monkeypatch.setenv("HOUR_LIMIT_SELECT_MEAL", "24")
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse("employees:meal_history_list")
    assert Meal.objects.filter(employee=user).count() == 1
