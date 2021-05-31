import pytest
from django.contrib.auth.models import Group

import factory
import factory.fuzzy

from ..models import Employee, Menu, MenuItem, User


class UserAdminFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Sequence(lambda n: f"john{n}")
    email = factory.Sequence(lambda n: f"lennon{n}@thebeatles.com")
    password = factory.PostGenerationMethodCall("set_password", "AbbeyRoad1969")
    user_type = User.ADMIN

    @factory.post_generation
    def has_default_group(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            default_group, _ = Group.objects.get_or_create(name="group")
            self.groups.add(default_group)


class UserEmployeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee

    user = factory.SubFactory(UserAdminFactory, user_type=User.EMPLOYEE)
    phone = factory.Faker("phone_number")


class MenuFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Menu

    id = factory.Faker("uuid4")
    name = factory.Faker("name")
    date = factory.Faker("date")
    additional_text = factory.Faker("text", max_nb_chars=100)


class MenuItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MenuItem

    description = factory.Faker("text", max_nb_chars=50)
    salad = True
    dessert = True
    order = factory.Faker("random_int")
    menu = factory.SubFactory(MenuFactory)
