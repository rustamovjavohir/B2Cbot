import re

import pytz
from telegram import (Update)
from telegram.ext import CallbackContext

from .keyboards import phone_keyboard, back_markup, inline, type_order, change_profile
from .models import B2CUser, B2CCommandText, B2CStep, B2COrder, B2CPrice


def phone_wrong(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = B2CUser.objects.filter(telegram_id=user_id).first()
    user.step = 1
    user.save()
    tex = B2CCommandText.objects.filter(text_code=1, lang_code=user.lang).first().text
    text = command_line(tex)
    context.bot.send_message(chat_id=user_id,
                             text=text,
                             reply_markup=phone_keyboard(user.lang))


def user_update(user_id, user_filed, update_text, step=0):
    commands = ["🔙Ortga", "sign up"]
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
        tex = B2CCommandText.objects.filter(text_code=2, lang_code=user.lang).first().text
        text = command_line(tex)
        update.message.reply_text(text=text, reply_markup=back_markup(user.lang))
    elif user.step == 5:
        create_order(update, context)
    elif user.step == 7:
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
        tex = B2CCommandText.objects.filter(text_code=2, lang_code=user.lang).first().text
        text = command_line(tex)
        update.message.reply_text(text=text, reply_markup=back_markup(user.lang))
    elif user.step == 5:
        create_order(update, context)
    elif user.step == 7:
        user = user_update(user_id, 'phone_number', phone_number, step=5)
        text = user_profile(user_id)
        context.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML", reply_markup=change_profile(user.lang))


def get_locations(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = B2CUser.objects.filter(telegram_id=user_id).first()
    if user.step == 5:
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
            text += f"<strong>Вес товаров: </strong>(необходимые)\n"
        else:
            text += f"<strong>Вес товаров: </strong>{step.weight}\n"
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
    else:
        if not step.order_name:
            text += f"<strong>Buyum nomi: </strong> (zarur)\n"
        else:
            text += f"<strong>Buyum nomi: </strong>{step.order_name}\n"
        if not step.weight:
            text += f"<strong>Buyum og'irligi: </strong>(zarur)\n"
        else:
            text += f"<strong>Buyum og'irligi: </strong>{step.weight}\n"
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
        elif step.step == 2:
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
            if msg:
                set_price(user_id, weight=msg, is_safe=step.is_safe)
                B2CStep.objects.filter(created_by=user_id).update(weight=msg)
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
        text = f"Имя: {user.first_name}\n" \
               f"Телефон номер: {user.phone_number}\n"
        if user.address:
            if "https" in user.address[:10]:
                text += f"<a href='{user.address}'> Локатсия</a>\n"
            else:
                text += f"Адрес: {user.address}\n"
        text += f"Язык: {user.lang}"
    else:
        text = f"Ism: {user.first_name}\n" \
               f"Telefon nomer: {user.phone_number}\n"
        if user.address:
            if "https" in user.address[:10]:
                text += f"<a href='{user.address}'> Локатсия</a>\n"
            else:
                text += f"Manzil: {user.address}\n"
        text += f"Til: {user.lang}"
    return text


def set_price(user_id, weight, is_safe):
    if weight:
        weight_list = [float(x) for x in re.findall(r'-?\d+\.?\d*', weight)]
        max_weight: float = max(weight_list)
        if is_safe:
            if max_weight <= 3:
                pr = B2CPrice.objects.all()[1].price1
            elif max_weight <= 6:
                pr = B2CPrice.objects.all()[1].price2
            elif max_weight <= 9:
                pr = B2CPrice.objects.all()[1].price3
            elif max_weight <= 12:
                pr = B2CPrice.objects.all()[1].price4
            elif max_weight <= 15:
                pr = B2CPrice.objects.all()[1].price5
            else:
                pr = B2CPrice.objects.all()[1].price6
        else:
            if max_weight <= 3:
                pr = B2CPrice.objects.all()[0].price1
            elif max_weight <= 6:
                pr = B2CPrice.objects.all()[0].price2
            elif max_weight <= 9:
                pr = B2CPrice.objects.all()[0].price3
            elif max_weight <= 12:
                pr = B2CPrice.objects.all()[0].price4
            elif max_weight <= 15:
                pr = B2CPrice.objects.all()[0].price5
            else:
                pr = B2CPrice.objects.all()[0].price6
        B2CStep.objects.filter(created_by=user_id).update(price=pr)
