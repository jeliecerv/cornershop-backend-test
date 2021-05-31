import pytest

from pytest_factoryboy import register

from meal_delivery.tests.factories import (
    MenuFactory,
    MenuItemFactory,
    UserAdminFactory,
    UserEmployeeFactory,
)

register(UserAdminFactory)
register(UserEmployeeFactory)
register(MenuFactory)
register(MenuItemFactory)


@pytest.fixture
def test_password():
    return "AbbeyRoad1969"


@pytest.fixture
def auto_login_user_admin(db, client, user_admin_factory, test_password):
    def make_auto_login(user=None):
        if user is None:
            user = user_admin_factory(password=test_password)
        client.login(username=user.username, password=test_password)
        return client, user

    return make_auto_login


@pytest.fixture
def auto_login_user_employee(db, client, user_employee_factory, test_password):
    def make_auto_login(employee=None):
        if employee is None:
            employee = user_employee_factory()
        client.login(username=employee.user.username, password=test_password)
        return client, employee

    return make_auto_login
