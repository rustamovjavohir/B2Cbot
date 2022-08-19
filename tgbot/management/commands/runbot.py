from django.conf import settings
from django.core.management import BaseCommand
from telegram import MessageEntity
from telegram.ext import (Updater, CallbackQueryHandler, Dispatcher, CommandHandler, Filters,
                          MessageHandler)

from tgbot.callback import keyboard_callback
from tgbot.utils import *
from tgbot.views import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        updater = Updater(settings.TELEGRAM_TOKEN)
        dispatcher: Dispatcher = updater.dispatcher
        updater.dispatcher.add_handler(CommandHandler(command='start', callback=start))
        dispatcher.add_handler(MessageHandler(Filters.regex(r"🔙Ortga") | Filters.regex(r"🔙Назад"), callback=back))
        dispatcher.add_handler(MessageHandler(Filters.regex(r"📝Qabul qilmoq") | Filters.regex(r"📝Принять"),
                                              callback=apply))
        dispatcher.add_handler(MessageHandler(Filters.regex(r"✅Tasdiqlash") | Filters.regex(r"✅Подтверждение"),
                                              callback=accept))
        dispatcher.add_handler(MessageHandler(Filters.location, callback=get_locations))
        dispatcher.add_handler(MessageHandler(Filters.text & Filters.entity(MessageEntity.PHONE_NUMBER),
                                              callback=phone_entity_handler))
        dispatcher.add_handler(MessageHandler(Filters.contact, callback=phone_contact_handler))
        dispatcher.add_handler(MessageHandler(Filters.all, callback=main_handler))
        updater.dispatcher.add_handler(CallbackQueryHandler(keyboard_callback))
        updater.start_polling()
        updater.idle()
