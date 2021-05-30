from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from ..decorators import admin_required
from ..forms import AdminSignUpForm, MenuItemFormset
from ..models import Menu, User


class AdminSignUpView(CreateView):
    model = User
    form_class = AdminSignUpForm
    template_name = "registration/signup_form.html"

    def get_context_data(self, **kwargs):
        kwargs["user_type"] = "admin"
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("admins:menu_list")


@method_decorator([login_required, admin_required], name="dispatch")
class MenuListView(ListView):
    model = Menu
    context_object_name = "menus"
    template_name = "meal_delivery/admins/menu_list.html"


@method_decorator([login_required, admin_required], name="dispatch")
class MenuCreateView(CreateView):
    model = Menu
    fields = ("name", "date", "additional_text")
    template_name = "meal_delivery/admins/menu_add_update_form.html"

    def get_context_data(self, **kwargs):
        if self.request.POST:
            kwargs["menu_items_form"] = MenuItemFormset(self.request.POST)
        else:
            kwargs["menu_items_form"] = MenuItemFormset()
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        menu = form.save(commit=False)
        menu.save()

        context = self.get_context_data()
        menu_items_form = context["menu_items_form"]
        if menu_items_form.is_valid():
            menu_items_form.instance = menu
            menu_items_form.save()

        messages.success(
            self.request,
            "The menu was created with success!",
        )
        return redirect("admins:menu_change", menu.pk)


class MenuUpdateView(UpdateView):
    model = Menu
    fields = ("name", "date", "additional_text")
    template_name = "meal_delivery/admins/menu_add_update_form.html"

    def get_context_data(self, **kwargs):
        if self.request.POST:
            kwargs["menu_items_form"] = MenuItemFormset(
                self.request.POST, instance=self.object
            )
        else:
            kwargs["menu_items_form"] = MenuItemFormset(instance=self.object)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        menu = form.save(commit=False)
        menu.save()

        context = self.get_context_data()
        menu_items_form = context["menu_items_form"]
        if menu_items_form.is_valid():
            menu_items_form.instance = menu
            menu_items_form.save()

        messages.success(
            self.request,
            "The menu was updated with success!",
        )
        return redirect("admins:menu_list")
