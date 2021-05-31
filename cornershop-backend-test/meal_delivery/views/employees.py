from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DetailView

from ..decorators import employee_required
from ..forms import EmployeeSignUpForm
from ..models import Employee, User, Meal, Menu, MenuItem
import datetime
from django.urls.base import reverse


class EmployeeSignUpView(CreateView):
    model = User
    form_class = EmployeeSignUpForm
    template_name = "registration/signup_form.html"

    def get_context_data(self, **kwargs):
        kwargs["user_type"] = "employee"
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("employees:meal_history_list")


@method_decorator([login_required, employee_required], name="dispatch")
class MealHistoryListView(ListView):
    model = Meal
    context_object_name = "meals"
    template_name = "meal_delivery/employees/meal_history_list.html"

    def get_context_data(self, **kwargs):
        today_menu = Menu.objects.filter(date=datetime.date.today()).first()
        now = datetime.datetime.now()
        if now.hour < 11:
            kwargs["today_menu"] = today_menu
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        employee = self.request.user.employee
        queryset = Meal.objects.filter(employee=employee)
        return queryset


@method_decorator([login_required, employee_required], name="dispatch")
class SelectMealView(DetailView):
    model = Menu
    template_name = "meal_delivery/employees/select_meal_form.html"

    def get_context_data(self, **kwargs):
        meal = Meal.objects.filter(
            employee=self.request.user.employee, menu_item__menu=self.object
        ).first()
        now = datetime.datetime.now()
        kwargs["meal"] = meal
        kwargs["is_editable"] = (
            datetime.date.today() == self.object.date and now.hour < 11
        )
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        data = request.POST

        now = datetime.datetime.now()
        if datetime.date.today() != self.object.date and now.hour > 11:
            messages.error(
                request,
                "It is not allowed to select a menu other than the one of the day!",
            )
            return redirect(
                reverse("employees:select_meal", kwargs={"pk": self.object.pk})
            )

        if data.get("meal_pk"):
            meal = Meal.objects.get(pk=data.get("meal_pk"))
        else:
            meal = Meal()

        meal.employee = request.user.employee
        meal.menu_item = MenuItem.objects.get(pk=data["menu_item"])
        meal.preference = data["preference"]
        meal.save()

        messages.success(
            request,
            "The menu was selected with success!",
        )
        return redirect("employees:meal_history_list")
