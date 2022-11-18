from telegram import Update
from telegram.ext import CallbackContext
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from B2CStaff.models import Kuryer, Dispatcher, Kuryer_step
from tgbot.models import LiveLocation, B2COrder, B2CUser


def is_kuryer(user_id):
    has = Kuryer.objects.filter(kuryer_telegram_id=user_id).exists()
    return has


def is_disp(user_id):
    has = Dispatcher.objects.filter(dispatcher_telegram_id=user_id).exists()
    return has


def inform(order):
    text = ''
    try:
        text += f"<strong>№: </strong>{order.id}\n"
        text += f"<strong>Товар: </strong>{order.order_name}\n"
        text += f"<strong>Способ доставки: </strong>{order.weight}\n"
        if "https" in order.from_location[:10]:
            text += f"<strong>Откуда доставить: </strong> <a href='{order.from_location}'>Локация1</a>\n"
        else:
            text += f"<strong>Откуда доставить: </strong>{order.from_location}\n"
        text += f"<strong>Имя отправителя: </strong>{order.sender_name}\n"
        text += f"<strong>Номер телефон отправителя: </strong>{order.sender_phone}\n"
        if "https" in order.to_location[:10]:
            text += f"<strong>Куда доставить: </strong> <a href='{order.to_location}'>Локация2</a>\n"
        else:
            text += f"<strong>Куда доставить: </strong>{order.to_location}\n"
        text += f"<strong>Имя получателя: </strong>{order.recipient_name}\n"
        text += f"<strong>Номер телефон получателя: </strong>{order.recipient_phone}\n"
        if order.comment:
            text += f"<strong>Комментарии: </strong>{order.comment}\n"
        if order.come_back:
            text += f"<strong>Обратно: </strong> ✅\n"
        else:
            text += f"<strong>Обратно: </strong> ❌\n"
        if order.price:
            text += f"<strong>Цена: </strong>{order.price} сум\n"
        return text
    except Exception as ex:
        print(ex)


def kuryer_text(kuryer, order_name, order_status):
    text = ""
    text += f"<strong>Курер: </strong>{kuryer.kuryer_name} \n" \
            f"<strong>Товар: </strong>{order_name}\n" \
            f"<strong>Статус: </strong>{order_status}\n"
    return text


def location(update: Update, context: CallbackContext):
    message = None
    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message
    current_pos = (update.effective_user.id, (message.location.latitude, message.location.longitude))

    loc_exist = LiveLocation.objects.filter(kuryer__kuryer_telegram_id=update.effective_user.id,
                                            is_delete=False).exists()
    print(loc_exist)
    if loc_exist:
        # LiveLocation.objects.filter(kuryer__kuryer_telegram_id=update.effective_user.id).update(
        #     latitude=message.location.latitude, longitude=message.location.longitude)
        locat = LiveLocation.objects.filter(kuryer__kuryer_telegram_id=update.effective_user.id).first()
        locat.latitude = message.location.latitude
        locat.longitude = message.location.longitude
        locat.save()
    else:
        kuryer = Kuryer.objects.filter(kuryer_telegram_id=update.effective_user.id).first()
        kuryer_step = Kuryer_step.objects.filter(admin_id=update.effective_user.id).first()
        order = B2COrder.objects.filter(id=kuryer_step.obj).first()
        client = B2CUser.objects.filter(telegram_id=order.created_by).first()
        live_location = LiveLocation.objects.create(kuryer=kuryer, order=order, client=client,
                                                    longitude=message.location.longitude,
                                                    latitude=message.location.latitude)
    print(message.message_id)

    print(current_pos)


def calendarCustom(update: Update, context: CallbackContext, callback, is_start=True):
    result, key, step = DetailedTelegramCalendar().process(callback.data)
    if is_start:
        text = "Start Date"
    else:
        text = "End Date"
    if not result and key:

        context.bot.edit_message_text(f"Select {LSTEP[step]}",
                                      callback.message.chat.id,
                                      callback.message.message_id,
                                      reply_markup=key)
    elif result:
        context.bot.edit_message_text(f"{text} {result}",
                                      callback.message.chat.id,
                                      callback.message.message_id)
        return result
