"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path

from .utils.healthz import healthz
from meal_delivery.views import meal_delivery, employees, admins

urlpatterns = [
    path("", include("meal_delivery.urls")),
    path("healthz", healthz, name="healthz"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/signup/", meal_delivery.SignUpView.as_view(), name="signup"),
    path(
        "accounts/signup/employee/",
        employees.EmployeeSignUpView.as_view(),
        name="employee_signup",
    ),
    path(
        "accounts/signup/admin/",
        admins.AdminSignUpView.as_view(),
        name="admin_signup",
    ),
]
