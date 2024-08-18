# telegrambot/management/commands/run_bot.py

from django.core.management.base import BaseCommand
from telegrambot.views import run_bot

class Command(BaseCommand):
    help = 'Run the Telegram bot'

    def handle(self, *args, **kwargs):
        run_bot()
