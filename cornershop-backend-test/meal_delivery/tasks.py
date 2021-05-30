import os

from celery.decorators import task
from celery.utils.log import get_task_logger

from slack import WebClient

from backend_test.envtools import getenv

from .models import Menu

logger = get_task_logger(__name__)
client = WebClient(token=getenv("SLACK_TOKEN"))


@task(name="send_menu_task")
def send_menu_task(menu_pk):
    """Celery task that executes sending the message to slack

    Args:
        menu_pk (string): identifier of the menu to be sent
    """
    logger.info(f"Start send menu to slack {menu_pk}")
    menu = Menu.objects.get(pk=menu_pk)
    menu.send_menu_slack(client)
    logger.info(f"End sended menu to slack {menu.name}")
