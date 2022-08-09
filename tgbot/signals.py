from django.conf import settings
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from telegram import InlineKeyboardButton, Bot, InlineKeyboardMarkup

from B2CStaff.models import Kuryer, Dispatcher
from B2CStaff.utils import inform, kuryer_text
from tgbot.models import B2COrder

staffbot = Bot(token=settings.TELEGRAM_TOKEN_B2CSTAFF)
userbot = Bot(token=settings.TELEGRAM_TOKEN)


@receiver(post_save, sender=B2COrder)
def post_save_order(sender, instance, created, *args, **kwargs):
    if created:
        kuryer = Kuryer.objects.filter(inwork=True, balance__gte=1).filter(
            ~Q(status=Kuryer.StatusKuryer.COURIER_ACCEPTED_ORDER))
        dispatcher = Dispatcher.objects.all()
        button = []
        for i in range(1, len(kuryer), 2):
            if len(kuryer) > 1:
                button.append({InlineKeyboardButton(f"{kuryer[i - 1].kuryer_name}",
                                                    callback_data=f"{instance.id}_{kuryer[i - 1].id}_kuryer"),
                               InlineKeyboardButton(f"{kuryer[i].kuryer_name}",
                                                    callback_data=f"{instance.id}_{kuryer[i].id}_kuryer")})
        if len(kuryer) % 2 == 1:
            button.append([InlineKeyboardButton(f"{kuryer[len(kuryer) - 1].kuryer_name}",
                                                callback_data=f"{instance.id}_{kuryer[len(kuryer) - 1].id}_kuryer")])

        button.append([InlineKeyboardButton(f"❌Отменить заказ",
                                            callback_data=f"{instance.id}_cancelapply")])

        for i in dispatcher:
            staffbot.send_message(chat_id=i.dispatcher_telegram_id, parse_mode="HTML",
                                  disable_web_page_preview=True,
                                  text=f"{inform(instance)}\n\nВыберите КУРЬЕР 👇",
                                  reply_markup=InlineKeyboardMarkup(button))


@receiver(pre_save, sender=B2COrder)
def pre_save_order(sender, instance, *args, **kwargs):
    try:
        previous = B2COrder.objects.get(id=instance.id)

        previous_kuryer = getattr(previous, "kuryer")
        if previous_kuryer != instance.kuryer:
            user_telegram_id = instance.created_by
            text = kuryer_text(instance.kuryer)
            userbot.send_message(chat_id=user_telegram_id, text=text, parse_mode="HTML", )

    except Exception as ex:
        pass
