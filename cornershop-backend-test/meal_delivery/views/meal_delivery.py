from django.shortcuts import redirect, render
from django.views.generic import TemplateView, DetailView
from django.http import Http404

from ..models import Menu


class SignUpView(TemplateView):
    template_name = "registration/signup.html"


def home(request):
    """Application entry point

    Args:
        request (request): data sent when invoking

    Returns:
        render|redirect: redirects to the corresponding page according to the type of user
    """
    if request.method == "POST":
        raise Http404("Page does not exist")
    if request.user.is_authenticated:
        if request.user.user_type == request.user.ADMIN:
            return redirect("admins:menu_list")
        else:
            return redirect("employees:meal_history_list")
    return render(request, "meal_delivery/home.html")


class MenuDetailView(DetailView):
    model = Menu
    template_name = "meal_delivery/menu_details.html"
