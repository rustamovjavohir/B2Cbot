from datetime import datetime, timezone

from django.conf import settings
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from telegram import Bot
from yaml import load

from tgbot.models import LiveLocation

staffbot = Bot(token=settings.TELEGRAM_TOKEN_B2CSTAFF)
userbot = Bot(token=settings.TELEGRAM_TOKEN)


@receiver(pre_save, sender=LiveLocation)
def pre_save_liveLocation(sender, instance, *args, **kwargs):
    if instance.id is None:
        message = userbot.send_location(chat_id=instance.client.telegram_id, longitude=instance.longitude,
                                        latitude=instance.latitude, live_period=28800)
        instance.send_message_id = message.message_id
        print(instance.send_message_id)
    else:
        try:
            print("update")
            previous = LiveLocation.objects.get(id=instance.id)
            if previous.latitude.__ne__(instance.latitude):
                print("new update")
                print(previous.message_id)
                message = userbot.edit_message_live_location(chat_id=instance.client.telegram_id,
                                                             message_id=instance.message_id,
                                                             longitude=instance.longitude,
                                                             latitude=instance.latitude)
                print(message.message_id, "original")
        except Exception as ex:
            print(ex)
            message = userbot.send_location(chat_id=instance.client.telegram_id, longitude=instance.longitude,
                                            latitude=instance.latitude, live_period=28800)
            instance.send_message_id = message.message_id
