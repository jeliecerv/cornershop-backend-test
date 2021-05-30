from django.shortcuts import redirect, render
from django.views.generic import TemplateView, DetailView

from ..models import Menu


class SignUpView(TemplateView):
    template_name = "registration/signup.html"


def home(request):
    if request.user.is_authenticated:
        if request.user.user_type == request.user.ADMIN:
            return redirect("admins:menu_list")
        else:
            return redirect("employees:meal_history_list")
    return render(request, "meal_delivery/home.html")


class MenuDetailView(DetailView):
    model = Menu
    template_name = "meal_delivery/menu_details.html"
