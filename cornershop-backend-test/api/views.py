import datetime

from rest_framework import mixins, permissions, viewsets
from rest_framework.exceptions import NotFound

from meal_delivery.models import Meal, Menu

from .authentication import (
    CustomUserAdminAuthentication,
    CustomUserEmployeeAuthentication,
)
from .serializers import MealSerializer, MenuSerializer


class AdminMenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    authentication_classes = [CustomUserAdminAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class TodayMenuViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    def get_queryset(self):
        menu = Menu.objects.filter(date=datetime.date.today())
        if len(menu) == 0:
            raise NotFound("today's menu is not available yet", 404)
        return menu


class ChooseTodayMenuMealViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer
    authentication_classes = [CustomUserEmployeeAuthentication]
    permission_classes = [permissions.IsAuthenticated]
