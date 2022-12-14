import re
from sms.views import checkValidMessage, sendValidMessage
import pytz
from telegram import (Update, ReplyKeyboardRemove)
from telegram.ext import CallbackContext
import phonenumbers

from .keyboards import phone_keyboard, back_markup, inline, type_order, change_profile, weight_type_button, \
    locations_button, sing_up_apply_markup, edit_order_markup, yes_or_no_button
from .models import B2CUser, B2CCommandText, B2CStep, B2COrder, B2CPrice


def phone_wrong(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = B2CUser.objects.filter(telegram_id=user_id).first()
    tex = B2CCommandText.objects.filter(text_code=1, lang_code=user.lang).first().text
    if user.step.__le__(6):
        user.step = 1
        user.save()
        text = command_line(tex)
        context.bot.send_message(chat_id=user_id,
                                 text=text,
                                 reply_markup=phone_keyboard(user.lang))
    else:
        text = tex.split('$')[-1]
        context.bot.send_message(chat_id=user_id,
                                 text=text,
                                 reply_markup=phone_keyboard(user.lang))


def user_update(user_id, user_filed, update_text, step=0):
    commands = ["🔙Ortga", "sign up", "🔙Назад"]
    # -----------------------------------------------------------------
    if update_text not in commands:
        user = B2CUser.objects.filter(telegram_id=user_id).first()
        setattr(user, user_filed, update_text)
        user.step = step
        user.save()
        return user


def phone_contact_handler(update: Update, context: CallbackContext):
    contact = update.message.contact
    user_id = update.effective_user.id
    user = B2CUser.objects.filter(telegram_id=user_id).first()
    step = B2CStep.objects.filter(created_by=user_id).first()
    if user.step == 1:
        user = user_update(user_id, 'phone_number', contact.phone_number, step=2)
        response = sendValidMessage(phone=contact.phone_number, user_telegram_id=user.telegram_id)
        tex = B2CCommandText.objects.filter(text_code=44, lang_code=user.lang).first().text
        text = command_line(tex)
        update.message.reply_text(text=text, reply_markup=back_markup(user.lang))
    elif user.step == 7:
        if step.step == 26:
            create_order_by_conversation(update, context)
        else:
            create_order(update, context)
    elif user.step == 9:
        user = user_update(user_id, 'phone_number', contact.phone_number, step=5)
        text = user_profile(user_id)
        context.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML", reply_markup=change_profile(user.lang))


def phone_entity_handler(update: Update, context: CallbackContext):
    phone_number_entity = phe = list(filter(lambda e: e.type == "phone_number", update.message.entities))[0]
    phone_number = update.message.text[phe.offset:phe.offset + phe.length]
    user_id = update.effective_user.id
    user = B2CUser.objects.filter(telegram_id=user_id).first()
    step = B2CStep.objects.filter(created_by=user_id).first()
    if user.step == 1:
        user = user_update(user_id, 'phone_number', phone_number, step=2)
        response = sendValidMessage(phone=phone_number, user_telegram_id=user.telegram_id)
        tex = B2CCommandText.objects.filter(text_code=44, lang_code=user.lang).first().text
        text = command_line(tex)
        update.message.reply_text(text=text, reply_markup=back_markup(user.lang))
    elif user.step == 7:
        if step.step == 26:
            create_order_by_conversation(update, context)
        else:
            create_order(update, context)
    elif user.step == 9:
        user = user_update(user_id, 'phone_number', phone_number, step=5)
        text = user_profile(user_id)
        context.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML", reply_markup=change_profile(user.lang))


def get_locations(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = B2CUser.objects.filter(telegram_id=user_id).first()
    if user.step == 7:
        user_location = update.message.location
        step = B2CStep.objects.filter(created_by=user_id).first()
        location = f"https://yandex.ru/maps/?pt={user_location.longitude},{user_location.latitude}&z=18&l=map"
        if step.step == 5:
            step.from_location = location
            step.save()
            create_order(update, context)
        elif step.step == 8:
            step.to_location = location
            step.save()
            create_order(update, context)
        elif step.step == 21:
            B2CStep.objects.filter(created_by=user_id).update(from_location=location)
            create_order_by_conversation(update, context)
        elif step.step == 24:
            B2CStep.objects.filter(created_by=user_id).update(to_location=location)
            create_order_by_conversation(update, context)


def wrong_full_name(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = B2CUser.objects.filter(telegram_id=user_id).first()
    tex = B2CCommandText.objects.filter(text_code=2, lang_code=user.lang).first().text
    text = command_line(tex)
    context.bot.send_message(chat_id=user_id,
                             text=text,
                             reply_markup=back_markup(user.lang))


def wrong_data_birthday(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = B2CUser.objects.filter(telegram_id=user_id).first()
    tex = B2CCommandText.objects.filter(text_code=6, lang_code=user.lang).first().text
    text = command_line(tex)
    # text = "Tu'g'ilgan sanangizni kiriting:\nmasalan  (31-12-2022)"
    context.bot.send_message(chat_id=user_id,
                             text=text,
                             reply_markup=back_markup(user.lang))


def command_line(text: str) -> str:
    text1 = text.split('$')
    tex = ''
    for item in text1:
        tex += item + "\n"
    return tex


def order_text(lang_code: str, user_id):
    text = ''
    step = B2CStep.objects.get(created_by=user_id)
    if lang_code.__eq__("ru"):
        if not step.order_name:
            text += f"<strong>Товар: </strong> (необходимые)\n"
        else:
            text += f"<strong>Товар: </strong>{step.order_name}\n"
        if not step.weight:
            text += f"<strong>Способ доставки: </strong>(необходимые)\n"
        else:
            text += f"<strong>Способ доставки: </strong>{step.weight}\n"
        if not step.from_location:
            text += f"<strong>Откуда доставить: </strong>(необходимые)\n"
        else:
            if "https" in step.from_location[:10]:
                text += f"<strong>Откуда доставить: </strong> <a href='{step.from_location}'>Локация1</a>\n"
            else:
                text += f"<strong>Откуда доставить: </strong>{step.from_location}\n"
        if not step.sender_name:
            text += f"<strong>Имя отправителя: </strong>(необходимые)\n"
        else:
            text += f"<strong>Имя отправителя: </strong>{step.sender_name}\n"
        if not step.sender_phone:
            text += f"<strong>Номер телефон отправителя: </strong>(необходимые)\n"
        else:
            text += f"<strong>Номер телефон отправителя: </strong>{step.sender_phone}\n"
        if not step.to_location:
            text += f"<strong>Куда доставить: </strong>(необходимые)\n"
        else:
            if "https" in step.to_location[:10]:
                text += f"<strong>Куда доставить: </strong> <a href='{step.to_location}'>Локация2</a>\n"
            else:
                text += f"<strong>Куда доставить: </strong>{step.to_location}\n"
        if not step.recipient_name:
            text += f"<strong>Имя получателя: </strong>(необходимые)\n"
        else:
            text += f"<strong>Имя получателя: </strong>{step.recipient_name}\n"
        if not step.recipient_phone:
            text += f"<strong>Номер телефон получателя: </strong>(необходимые)\n"
        else:
            text += f"<strong>Номер телефон получателя: </strong>{step.recipient_phone}\n"
        if not step.comment:
            text += f"<strong>Комментарии: </strong>(необязательный)\n"
        else:
            text += f"<strong>Комментарии: </strong>{step.comment}\n"
        if not step.come_back:
            text += f"<strong>Обратно: </strong> ❌\n"
        else:
            text += f"<strong>Обратно: </strong> ✅\n"
        if step.price:
            text += f"<strong>Цена: </strong>{step.price} сум\n"
        text += "\n<strong>☝️Если всё правилно нажмите '📤Отправить'\n" \
                "Иначе отредактируйте</strong>"
    else:
        if not step.order_name:
            text += f"<strong>Buyum nomi: </strong> (zarur)\n"
        else:
            text += f"<strong>Buyum nomi: </strong>{step.order_name}\n"
        if not step.weight:
            text += f"<strong>Yetkazib berish usuli: </strong>(zarur)\n"
        else:
            text += f"<strong>Yetkazib berish usuli: </strong>{step.weight}\n"
        if not step.from_location:
            text += f"<strong>Qayerdan olish: </strong>(zarur)\n"
        else:
            if "https" in step.from_location[:10]:
                text += f"<strong>Qayerdan olish: </strong> <a href='{step.from_location}'>Manzil1</a>\n"
            else:
                text += f"<strong>Qayerdan olish: </strong>{step.from_location}\n"
        if not step.sender_name:
            text += f"<strong>Yuboruvchining ismi: </strong>(zarur)\n"
        else:
            text += f"<strong>Yuboruvchining ismi: </strong>{step.sender_name}\n"
        if not step.sender_phone:
            text += f"<strong>Yuboruvchining nomeri: </strong>(zarur)\n"
        else:
            text += f"<strong>Yuboruvchining nomeri: </strong>{step.sender_phone}\n"
        if not step.to_location:
            text += f"<strong>Qayerga yetkazish: </strong>(zarur)\n"
        else:
            if "https" in step.to_location[:10]:
                text += f"<strong>Qayerga yetkazish: </strong> <a href='{step.to_location}'>Manzil2</a>\n"
            else:
                text += f"<strong>Qayerga yetkazish: </strong>{step.to_location}\n"
        if not step.recipient_name:
            text += f"<strong>Qabul qiluvchining ismi: </strong>(zarur)\n"
        else:
            text += f"<strong>Qabul qiluvchining ismi: </strong>{step.recipient_name}\n"
        if not step.recipient_phone:
            text += f"<strong>Qabul qiluvchining nomeri: </strong>(zarur)\n"
        else:
            text += f"<strong>Qabul qiluvchining nomeri: </strong>{step.recipient_phone}\n"
        if not step.comment:
            text += f"<strong>Izoh: </strong>(xohishiy)\n"
        else:
            text += f"<strong>Izoh: </strong>{step.comment}\n"
        if not step.come_back:
            text += f"<strong>Qaytib kelish: </strong> ❌\n"
        else:
            text += f"<strong>Qaytib kelish: </strong> ✅\n"
        if step.price:
            text += f"<strong>Narx: </strong>{step.price} сум\n"
        text += "\n<strong>☝️Ma'lumotlar to'g'ri bo'lsa '📤Jo'natish' tugmasini bosing\n" \
                "Aks holda tahrirlang</strong>"
    return text


def create_order(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = B2CUser.objects.get(telegram_id=user_id)
    step = B2CStep.objects.filter(created_by=user_id).first()
    set_price(user_id, weight=step.weight, is_safe=step.is_safe)
    try:
        msg = update.message.text
    except Exception as ex:
        msg = None
    try:
        if is_back(msg=msg):
            try:
                context.bot.delete_message(chat_id=user_id, message_id=step.delete_message)
            except Exception as ex:
                print(ex)
            update.message.delete()
            text = order_text(user.lang, user_id)
            update.message.reply_html(text, disable_web_page_preview=True, reply_markup=inline(user.lang))
        if step.step.__le__(5):
            if step.step == 2:
                text = order_text(user.lang, user_id)
                context.bot.send_message(chat_id=user_id, text=text, parse_mode='HTML', disable_web_page_preview=True,
                                         reply_markup=inline(user.lang))
            elif step.step == 3:
                try:
                    context.bot.delete_message(chat_id=user_id, message_id=step.delete_message)
                except Exception as ex:
                    print(ex)
                update.message.delete()
                msg = update.message.text
                B2CStep.objects.filter(created_by=user_id).update(order_name=msg)
                text = order_text(user.lang, user_id)
                update.message.reply_html(text, disable_web_page_preview=True, reply_markup=inline(user.lang))
            elif step.step == 4:
                try:
                    context.bot.delete_message(chat_id=user_id, message_id=step.delete_message)
                except Exception as ex:
                    print(ex)
                update.message.delete()
                msg = update.message.text
                try:
                    if msg:
                        set_price(user_id, weight=msg, is_safe=step.is_safe)
                        B2CStep.objects.filter(created_by=user_id).update(weight=msg)
                except Exception as ex:
                    pass
                    # weight_text = B2CCommandText.objects.get(text_code=25, lang_code=user.lang).text
                    # context.bot.send_message(chat_id=user_id, text=weight_text,
                    #                          reply_markup=weight_type_button(user.lang))
                text = order_text(user.lang, user_id)
                update.message.reply_html(text, disable_web_page_preview=True, reply_markup=inline(user.lang))
            elif step.step == 5:
                try:
                    context.bot.delete_message(chat_id=user_id, message_id=step.delete_message)
                except Exception as ex:
                    print(ex)
                update.message.delete()
                msg = update.message.text
                if msg:
                    B2CStep.objects.filter(created_by=user_id).update(from_location=msg)
                text = order_text(user.lang, user_id)
                update.message.reply_html(text, disable_web_page_preview=True, reply_markup=inline(user.lang))
        elif step.step == 6:
            try:
                context.bot.delete_message(chat_id=user_id, message_id=step.delete_message)
            except Exception as ex:
                print(ex)
            update.message.delete()
            msg = update.message.text
            B2CStep.objects.filter(created_by=user_id).update(sender_name=msg)
            text = order_text(user.lang, user_id)
            update.message.reply_html(text, disable_web_page_preview=True, reply_markup=inline(user.lang))
        elif step.step == 7:
            try:
                context.bot.delete_message(chat_id=user_id, message_id=step.delete_message)
            except Exception as ex:
                print(ex)
            update.message.delete()
            msg = update.message.text
            if update.message.contact:
                msg = update.message.contact.phone_number
            B2CStep.objects.filter(created_by=user_id).update(sender_phone=msg)
            text = order_text(user.lang, user_id)
            update.message.reply_html(text, disable_web_page_preview=True, reply_markup=inline(user.lang))
        elif step.step == 8:
            try:
                context.bot.delete_message(chat_id=user_id, message_id=step.delete_message)
            except Exception as ex:
                print(ex)
            update.message.delete()
            msg = update.message.text
            if msg:
                B2CStep.objects.filter(created_by=user_id).update(to_location=msg)
            text = order_text(user.lang, user_id)
            update.message.reply_html(text, disable_web_page_preview=True, reply_markup=inline(user.lang))
        elif step.step == 9:
            try:
                context.bot.delete_message(chat_id=user_id, message_id=step.delete_message)
            except Exception as ex:
                print(ex)
            update.message.delete()
            msg = update.message.text
            B2CStep.objects.filter(created_by=user_id).update(recipient_name=msg)
            text = order_text(user.lang, user_id)
            update.message.reply_html(text, disable_web_page_preview=True, reply_markup=inline(user.lang))
        elif step.step == 10:
            try:
                context.bot.delete_message(chat_id=user_id, message_id=step.delete_message)
            except Exception as ex:
                print(ex)
            update.message.delete()
            msg = update.message.text
            if update.message.contact:
                msg = update.message.contact.phone_number
            B2CStep.objects.filter(created_by=user_id).update(recipient_phone=msg)
            text = order_text(user.lang, user_id)
            update.message.reply_html(text, disable_web_page_preview=True, reply_markup=inline(user.lang))
        elif step.step == 11:
            try:
                context.bot.delete_message(chat_id=user_id, message_id=step.delete_message)
            except Exception as ex:
                print(ex)
            update.message.delete()
            msg = update.message.text
            B2CStep.objects.filter(created_by=user_id).update(comment=msg)
            text = order_text(user.lang, user_id)
            update.message.reply_html(text, disable_web_page_preview=True, reply_markup=inline(user.lang))
    except Exception as ex:
        print(ex)


def my_orders(lang_code, user_id):
    orders = B2COrder.objects.filter(created_by=user_id, is_deleted=False).order_by('id')
    orders_list = []
    data, product, weight, order_from, name_sender, phone_sender, order_to, name_receiver, phone_receiver, comment, \
    status = "Дата", "Товар", "Вес товаров", "Откуда доставить", "Имя отправителя", "Номер телефон отправителя", \
             "Куда доставить", "Имя получателя", "Номер телефон получателя", "Комментарии", "Стватус"

    if lang_code.__eq__("uz"):
        data, product, weight, order_from, name_sender, phone_sender, order_to, name_receiver, phone_receiver, comment, \
        status = "Vaqt", "Mahsulot", "Mahsulot og'irligi", "Qayerdan olish", "Yuboruvchining ismi", \
                 "Yuboruvchining nomeri", "Qayerga yetkazish", "Qabul qiluvchining ismi", "Qabul qiluvchining nomeri", \
                 "Izoh", "Status"
    for i, order in enumerate(orders):
        text = ''
        text += f"<strong>№: </strong>{order.id}\n"
        text += f"<strong>{data}: </strong>" \
                f"{order.created_at.astimezone(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += f"<strong>{product}: </strong>{order.order_name}\n"
        text += f"<strong>{weight}: </strong>{order.weight}\n"
        if "https" in order.from_location[:10]:
            text += f"<strong>{order_from}: </strong> <a href='{order.from_location}'>Локация1</a>\n"
        else:
            text += f"<strong>{order_from}: </strong>{order.from_location}\n"
        text += f"<strong>{name_sender}: </strong>{order.sender_name}\n"
        text += f"<strong>{phone_sender}: </strong>{order.sender_phone}\n"
        if "https" in order.to_location[:10]:
            text += f"<strong>{order_to}: </strong> <a href='{order.to_location}'>Локация2</a>\n"
        else:
            text += f"<strong>{order_to}: </strong>{order.to_location}\n"
        text += f"<strong>{name_receiver}: </strong>{order.recipient_name}\n"
        text += f"<strong>{phone_receiver}: </strong>{order.recipient_phone}\n"
        text += f"<strong>{comment}: </strong>{order.comment}\n" if order.comment else ""
        text += f"<strong>{status}: </strong>{order.status}" if order.status else ""
        orders_list.append(text)
    return orders_list


def is_back(msg) -> bool:
    return msg in ["🔙Ortga", "🔙Назад", "🔙Back"]


def is_apply(msg) -> bool:
    return msg in ["✅Подтверждение", "✅Tasdiqlash"]


def type_order_util(update, context):
    user_id = update.effective_user.id
    step = B2CStep.objects.filter(created_by=user_id).first()
    user = B2CUser.objects.filter(telegram_id=user_id).first()
    if step.step == 1:
        step.step = 2
        step.save()
        # Buyurtma turini tanlang
        order_type_text = B2CCommandText.objects.get(text_code=21, lang_code=user.lang).text
        msg = context.bot.send_message(chat_id=user.telegram_id, text=order_type_text,
                                       reply_markup=type_order(user.lang))
        user.del_message = msg.message_id

        #  -----------------
        user.save()


def user_profile(user_id):
    user = B2CUser.objects.get(telegram_id=user_id)
    if user.lang.__eq__("ru"):
        text = f"\n<strong>Ваша информация:</strong>"
        text += f"\n<strong>Ваше имя : </strong>{user.first_name}" \
                f"\n<strong>Ваш номер телефона : </strong>{user.phone_number}"
        if user.address:
            if "https" in user.address[:10]:
                text += f"\n<strong>Адрес: </strong><a href='{user.address}'> Локатсия</a>"
            else:
                text += f"\n<strong>Адрес: </strong>{user.address}"
        text += f"\n<strong>Твоя дата рождения : </strong>{user.data_birthday}" \
                f"\n<strong>Язык: </strong>{user.lang}"

    else:
        text = f"<strong>Ma'lumotlaringiz</strong>"
        text += f"\n<strong>Ism: </strong>{user.first_name}" \
                f"\n<strong>Telefon nomeringiz : </strong>{user.phone_number}"
        if user.address:
            if "https" in user.address[:10]:
                text += f"\n<strong>Manzil: </strong><a href='{user.address}'> Locatsiya</a>"
            else:
                text += f"\n<strong>Manzil: </strong>{user.address}"
        text += f"\n<strong>Tu'g'ilgan sanangiz : </strong>{user.data_birthday}" \
                f"\n<strong>Til: </strong>{user.lang}"

    return text


def set_price(user_id, weight, is_safe):
    try:
        if weight:
            is_come_back = B2CStep.objects.get(created_by=user_id).come_back
            weight_list = [float(x) for x in re.findall(r'-?\d+\.?\d*', weight)]
            max_weight: float = max(weight_list)
            if is_safe:
                if max_weight <= 10:
                    pr = B2CPrice.objects.all()[1].price1
                elif max_weight <= 20:
                    pr = B2CPrice.objects.all()[1].price2
                else:
                    pr = B2CPrice.objects.all()[1].price3
                if is_come_back:
                    pr += B2CPrice.objects.all()[1].price_come_back
            else:
                if max_weight <= 10:
                    pr = B2CPrice.objects.all()[0].price1
                elif max_weight <= 20:
                    pr = B2CPrice.objects.all()[0].price2
                else:
                    pr = B2CPrice.objects.all()[0].price3
                if is_come_back:
                    pr += B2CPrice.objects.all()[0].price_come_back
            B2CStep.objects.filter(created_by=user_id).update(price=pr)
    except Exception as ex:
        print(ex, " --set_price")


def go_create_order_by_conversation(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = B2CUser.objects.get(telegram_id=user_id)
    B2CStep.objects.filter(created_by=user_id).update(step=21)
    order_from_text = B2CCommandText.objects.filter(text_code=26, lang_code=user.lang).first().text
    context.bot.send_message(chat_id=user_id, text=order_from_text,
                             reply_markup=locations_button(user.lang))


def create_order_by_conversation(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = B2CUser.objects.get(telegram_id=user_id)
    step = B2CStep.objects.get(created_by=user_id)
    msg = update.message.text
    if step.step.__eq__(21):
        step.step = 22
        step.save()
        if msg and not is_back(msg) and not is_apply(msg):
            B2CStep.objects.filter(created_by=user_id).update(from_location=msg)
        order_name_text = B2CCommandText.objects.get(text_code=24, lang_code=user.lang).text
        #  Mahsulot nomini kiriting
        context.bot.send_message(chat_id=user_id, text=order_name_text, disable_web_page_preview=True,
                                 reply_markup=back_markup(user.lang))
    elif step.step.__eq__(22):
        step.step = 23
        step.save()
        if not is_back(msg):
            B2CStep.objects.filter(created_by=user_id).update(order_name=msg)
        order_weight_text = B2CCommandText.objects.get(text_code=25, lang_code=user.lang).text
        # Mahsulot vaznini tanlang (kg)⤵️
        context.bot.send_message(chat_id=user_id, text=order_weight_text, disable_web_page_preview=True,
                                 reply_markup=weight_type_button(user.lang))
    elif step.step.__eq__(23):
        try:
            weight_list = [float(x) for x in re.findall(r'-?\d+\.?\d*', msg)]
            if not is_back(msg) and len(weight_list):
                step.step = 24
                step.save()
                set_price(user_id, weight=msg, is_safe=step.is_safe)
                B2CStep.objects.filter(created_by=user_id).update(weight=msg)
                to_location_text = B2CCommandText.objects.get(text_code=29, lang_code=user.lang).text
                # Qayerga yetkazib berish, manzilni yuboring
                context.bot.send_message(chat_id=user_id, text=to_location_text, disable_web_page_preview=True,
                                         reply_markup=locations_button(user.lang))
        except Exception as ex:
            print(ex, "--step 23")
    elif step.step.__eq__(24):
        step.step = 25
        step.save()
        if msg and not is_back(msg):
            B2CStep.objects.filter(created_by=user_id).update(to_location=msg)
        recipient_name_text = B2CCommandText.objects.get(text_code=30, lang_code=user.lang).text
        # Qabul qiluvchining ismini kiriitng
        context.bot.send_message(chat_id=user_id, text=recipient_name_text, reply_markup=back_markup(user.lang))
    elif step.step.__eq__(25):
        step.step = 26
        step.save()
        if not is_back(msg):
            B2CStep.objects.filter(created_by=user_id).update(recipient_name=msg)
        recipient_phone_text = B2CCommandText.objects.get(text_code=31, lang_code=user.lang).text
        # text = "Qabul qiluvchining nomerini kiriitng"
        context.bot.send_message(chat_id=user_id, text=recipient_phone_text, reply_markup=phone_keyboard(user.lang))
    elif step.step.__eq__(26):
        step.step = 27
        step.save()
        try:
            if update.message.contact:
                msg = update.message.contact.phone_number
            if not is_back(msg):
                phone_number = phonenumbers.parse(msg, region='UZ')
                if phonenumbers.is_valid_number(phone_number):
                    B2CStep.objects.filter(created_by=user_id).update(recipient_phone=msg)
                else:
                    raise Exception("Wrong number")
            # text = "Qaytib olib kelishni hohlaysizmi "
            return_service_text = B2CCommandText.objects.get(text_code=40, lang_code=user.lang).text
            context.bot.send_message(chat_id=user_id, text=return_service_text,
                                     reply_markup=yes_or_no_button(user.lang))
        except Exception as ex:
            B2CStep.objects.filter(created_by=user_id).update(step=26)
            phone_wrong(update, context)
            print(ex, "--wrong phone")
    elif step.step.__eq__(27):
        step.step = 28
        step.save()
        # update.message.delete()
        context.bot.send_message(chat_id=user_id, text="Thank you", reply_markup=ReplyKeyboardRemove())
        if not is_back(msg):
            if msg.__eq__("Да") or msg.__eq__("Ha"):
                B2CStep.objects.filter(created_by=user_id).update(come_back=True)
            else:
                B2CStep.objects.filter(created_by=user_id).update(come_back=False)
        text = order_text(user.lang, user_id)
        update.message.reply_html(text, disable_web_page_preview=True, reply_markup=edit_order_markup(user.lang))
