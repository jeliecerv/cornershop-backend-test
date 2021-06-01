import datetime

from rest_framework import serializers

from backend_test.envtools import getenv
from meal_delivery.models import Meal, Menu, MenuItem


class MenuItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "description", "salad", "dessert", "order"]


class MenuSerializer(serializers.HyperlinkedModelSerializer):
    items = MenuItemSerializer(many=True)

    class Meta:
        model = Menu
        fields = ["id", "name", "date", "additional_text", "items"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        menu = Menu.objects.create(**validated_data)
        for item_data in items_data:
            MenuItem.objects.create(menu=menu, **item_data)
        return menu

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items")
        menu = super().update(instance, validated_data)
        for item_data in items_data:
            MenuItem.objects.update_or_create(menu=menu, **item_data)

        return menu


class MealSerializer(serializers.HyperlinkedModelSerializer):
    menu_item_id = serializers.IntegerField()

    class Meta:
        model = Meal
        fields = ["menu_item_id", "preference"]

    def validate_menu_item_id(self, value):
        menu_item = MenuItem.objects.filter(
            menu__date=datetime.date.today(), pk=value
        ).first()
        if not menu_item:
            raise serializers.ValidationError("Is not a valid meal option")
        now = datetime.datetime.now()
        if now.hour > int(getenv("HOUR_LIMIT_SELECT_MEAL", default=11)):
            raise serializers.ValidationError(
                "It is no longer allowed to select a meal from today's menu"
            )
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        meal = Meal.objects.create(employee=user.employee, **validated_data)
        return meal
