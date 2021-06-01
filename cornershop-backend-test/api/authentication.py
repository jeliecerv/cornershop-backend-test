from meal_delivery.models import User
from rest_framework import authentication
from rest_framework import exceptions


class CustomUserAdminAuthentication(authentication.BasicAuthentication):
    def authenticate(self, request):
        user, _ = super().authenticate(request)
        if user.user_type != User.ADMIN:
            raise exceptions.AuthenticationFailed("User is not an admin.")
        return user, _


class CustomUserEmployeeAuthentication(authentication.BasicAuthentication):
    def authenticate(self, request):
        user, _ = super().authenticate(request)
        if user.user_type != User.EMPLOYEE:
            raise exceptions.AuthenticationFailed("User is not an employee.")
        return user, _
