import datetime
import logging
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from slack.errors import SlackApiError

from backend_test.envtools import getenv

logger = logging.getLogger(__name__)


class User(AbstractUser):
    ADMIN = 1
    EMPLOYEE = 2
    USER_TYPE_CHOICES = (
        (ADMIN, "admin"),
        (EMPLOYEE, "employee"),
    )

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone = models.CharField(max_length=20)

    class Meta:
        ordering = ["user__last_name"]
        verbose_name_plural = "employees"


class Menu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=24, unique=True, verbose_name="menu name")
    date = models.DateField(default=datetime.date.today)
    additional_text = models.CharField(max_length=128, null=True, blank=True)

    def send_menu_slack(self, client):
        message = """
            Hello!
            I share with you today's menu [{date_menu}] :)

            {options}

            Have a nice day!
        """
        options = []
        for item in self.items.all():
            option_text = f"Option {item.order + 1}: {item.description}{', salad' if item.salad else ''}{', dessert' if item.dessert else ''}"
            options.append(option_text)
        try:
            message = message.format(date_menu=self.date, options="\n".join(options))
            response = client.chat_postMessage(
                channel=getenv("SLACK_CHANNEL"), text=message
            )
            logger.info(response["message"]["text"])
        except SlackApiError as e:
            logger.error(f"Got an error: {e.response['error']}")
        except Exception as e:
            logger.error(f"Got an error: {e}")

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "menus"

    def __unicode__(self):
        return f"{self.date}: {self.name}"


class MenuItem(models.Model):
    description = models.CharField(max_length=128)
    salad = models.BooleanField(default=True, verbose_name="salad?")
    dessert = models.BooleanField(default=True, verbose_name="dessert?")
    order = models.PositiveSmallIntegerField(default=0)

    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="items")
    meal = models.ManyToManyField(Employee, through="Meal", related_name="items")

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "menu items"

    def __unicode__(self):
        return f"{self.order}: {self.menu} - {self.description}"


class Meal(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="meals"
    )
    menu_item = models.ForeignKey(
        MenuItem, on_delete=models.CASCADE, related_name="meals"
    )
    date_choose = models.DateTimeField(auto_now_add=True)
    preference = models.CharField(max_length=128)

    class Meta:
        ordering = ["-date_choose"]
        verbose_name_plural = "meals"

    def __unicode__(self):
        return f"{self.date_choose}: {self.menu_item}"
