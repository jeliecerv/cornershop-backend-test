import datetime

import pytest

from meal_delivery.models import Meal
from meal_delivery.tests.fixtures import *


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def api_client_with_credentials(db, user_admin_factory, api_client):
    user = user_admin_factory()
    api_client.force_authenticate(user=user)
    yield api_client
    api_client.force_authenticate(user=None)


@pytest.fixture
def api_client_with_credentials_employee(db, user_employee_factory, api_client):
    employee = user_employee_factory()
    api_client.force_authenticate(user=employee.user)
    yield api_client
    api_client.force_authenticate(user=None)


@pytest.fixture
def menu_data():
    data = {
        "name": "Menu Help!",
        "date": "2021-06-01",
        "additional_text": "Beats 1965",
        "items": [
            {
                "description": "The Night Before",
                "salad": True,
                "dessert": True,
                "order": 0,
            },
            {"description": "Help!", "salad": True, "dessert": False, "order": 1},
            {
                "description": "Tell me what you see",
                "salad": True,
                "dessert": True,
                "order": 2,
            },
        ],
    }
    return data


@pytest.mark.django_db
def test_today_menu_without_menu(api_client):
    url = "/api/today-menu/"
    response = api_client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_today_menu_with_menu(api_client, menu_factory, menu_item_factory):
    menu = menu_factory(date=datetime.date.today())
    menu_item_factory(menu=menu)
    menu_item_factory(menu=menu)
    menu_item_factory(menu=menu)

    url = "/api/today-menu/"
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == menu.id


@pytest.mark.django_db
def test_list_menu_unauthorize(api_client, menu_factory):
    menu_factory()
    menu_factory()

    url = "/api/admin-menu/"
    response = api_client.get(url)
    assert response.status_code == 401
    assert len(response.json()) == 0


@pytest.mark.django_db
def test_list_menu_authorize(api_client_with_credentials, menu_factory):
    menu_factory()
    menu_factory()

    url = "/api/admin-menu/"
    response = api_client_with_credentials.get(url)
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.django_db
def test_get_menu_authorize(api_client_with_credentials, menu_factory):
    menu = menu_factory()

    url = f"/api/admin-menu/{menu.pk}/"
    response = api_client_with_credentials.get(url)
    assert response.status_code == 200
    assert response.json()["id"] == menu.pk


@pytest.mark.django_db
def test_create_menu(api_client_with_credentials, menu_data):
    url = f"/api/admin-menu/"
    response = api_client_with_credentials.post(url, data=menu_data, format="json")
    assert response.status_code == 201
    assert response.json()["name"] == menu_data["name"]


@pytest.mark.django_db
def test_update_menu(api_client_with_credentials, menu_factory, menu_data):
    menu = menu_factory()
    assert menu.name != menu_data["name"]
    url = f"/api/admin-menu/{menu.pk}/"
    response = api_client_with_credentials.put(url, data=menu_data, format="json")
    assert response.status_code == 200
    assert response.json()["name"] == menu_data["name"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "date, hour_limit, status_code",
    [
        (datetime.date.today(), 24, 201),
        (datetime.date.today() - datetime.timedelta(days=1), 24, 400),
        (datetime.date.today(), 0, 400),
    ],
)
def test_choose_today_menu_meal(
    monkeypatch,
    date,
    hour_limit,
    status_code,
    api_client_with_credentials_employee,
    menu_factory,
    menu_item_factory,
):
    menu = menu_factory(date=date)
    menu_item = menu_item_factory(menu=menu)
    menu_item_factory(menu=menu)
    menu_item_factory(menu=menu)

    monkeypatch.setenv("HOUR_LIMIT_SELECT_MEAL", str(hour_limit))

    data = {"menu_item_id": menu_item.pk, "preference": "Let it be"}
    url = "/api/choose-today-menu-meal/"
    response = api_client_with_credentials_employee.post(url, data=data, format="json")
    assert response.status_code == status_code
