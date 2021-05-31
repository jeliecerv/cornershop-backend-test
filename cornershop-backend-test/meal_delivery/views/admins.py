from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView

from ..decorators import admin_required
from ..forms import AdminSignUpForm, MenuItemFormset
from ..models import Menu, User
from ..tasks import send_menu_task


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


class BaseMenuView(object):
    """Base view to update and create menus"""

    model = Menu
    fields = ("name", "date", "additional_text")
    template_name = "meal_delivery/admins/menu_add_update_form.html"

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
            "The menu was created/updated with success!",
        )
        send_menu_task.delay(menu.pk)
        return redirect("admins:menu_list")


@method_decorator([login_required, admin_required], name="dispatch")
class MenuCreateView(BaseMenuView, CreateView):
    def get_context_data(self, **kwargs):
        if self.request.POST:
            kwargs["menu_items_form"] = MenuItemFormset(self.request.POST)
        else:
            kwargs["menu_items_form"] = MenuItemFormset()
        return super().get_context_data(**kwargs)


@method_decorator([login_required, admin_required], name="dispatch")
class MenuUpdateView(BaseMenuView, UpdateView):
    def get_context_data(self, **kwargs):
        if self.request.POST:
            kwargs["menu_items_form"] = MenuItemFormset(
                self.request.POST, instance=self.object
            )
        else:
            kwargs["menu_items_form"] = MenuItemFormset(instance=self.object)
        return super().get_context_data(**kwargs)
