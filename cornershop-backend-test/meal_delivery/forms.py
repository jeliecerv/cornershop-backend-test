from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.models import inlineformset_factory
from django.forms.utils import ValidationError

from .models import Employee, Menu, MenuItem, User


class AdminSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta(UserCreationForm.Meta):
        model = User

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = User.ADMIN
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        if commit:
            user.save()
        return user


class EmployeeSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    phone = forms.CharField(max_length=20)

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.user_type = User.EMPLOYEE
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.save()
        employee = Employee.objects.create(user=user)
        employee.phone = self.cleaned_data.get("phone")
        employee.save()
        return user


MenuItemFormset = inlineformset_factory(
    Menu,
    MenuItem,
    fields=("order", "description", "salad", "dessert"),
    extra=1,
    widgets={"order": forms.HiddenInput()},
)
