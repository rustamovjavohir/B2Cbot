from django.conf import settings
from django.core.management import BaseCommand
from telegram.ext import (Updater, Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, Filters)

from B2CStaff.callback import keyboard_callback
from B2CStaff.utils import location
from B2CStaff.views import start, main_handler


class Command(BaseCommand):
    def handle(self, *args, **options):
        updater = Updater(settings.TELEGRAM_TOKEN_B2CSTAFF)
        dispatcher: Dispatcher = updater.dispatcher
        updater.dispatcher.add_handler(CommandHandler(command='start', callback=start))
        dispatcher.add_handler(MessageHandler(Filters.location, location))
        dispatcher.add_handler(MessageHandler(Filters.all, callback=main_handler))
        updater.dispatcher.add_handler(CallbackQueryHandler(keyboard_callback))
        updater.start_polling()
        updater.idle()
