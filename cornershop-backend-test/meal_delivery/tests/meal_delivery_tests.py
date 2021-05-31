import uuid

import pytest
from django.urls import resolve, reverse

from pytest_factoryboy import register

from meal_delivery.tests.factories import MenuFactory

register(MenuFactory)


def test_home_view(client):
    url = reverse("home")
    response = client.get(url)
    assert response.status_code == 200


def test_home_post_view(client):
    url = reverse("home")
    response = client.post(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_menu_detail_wrong_view(client):
    wrong_uuid = uuid.uuid4()
    url = reverse("menu_detail", kwargs={"pk": wrong_uuid})
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_menu_detail_right_view(client, menu_factory):
    menu = menu_factory()
    url = reverse("menu_detail", kwargs={"pk": menu.pk})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_access_admin_view_no_signup(client):
    url = reverse("admins:menu_list")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={url}"


@pytest.mark.django_db
def test_access_employee_view_no_signup(client):
    url = reverse("employees:meal_history_list")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={url}"
