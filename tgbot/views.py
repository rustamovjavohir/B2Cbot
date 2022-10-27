# Create your views here.

import re

from telegram import Update
from telegram.ext import CallbackContext

from sms.models import Sms
from sms.views import checkValidMessage
from tgbot.keyboards import language_inline_button, phone_keyboard, sing_up_apply_markup, type_delivery, \
    order_markup, change_profile, back_markup, del_order_inline_button, apply_button
from tgbot.models import B2CUser, B2CCommandText, B2CStep
from tgbot.utils import command_line, user_update, phone_wrong, wrong_full_name, wrong_data_birthday, create_order, \
    my_orders, user_profile, create_order_by_conversation, go_create_order_by_conversation


def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    username = update.effective_user.username
    full_name = update.effective_user.full_name

    user = B2CUser.objects.get_or_create(telegram_id=user_id, username=f"@{username}", full_name=full_name)[0]

    try:
        update.message.delete()
    except Exception as ex:
        print(f"{ex} \n------------  (start, menu) message topilmadi")

    if not user.is_active:
        user.step = 0
        user.save()
        update.message.reply_text(f"Xush Kelibsiz"
                                  f"\nO'zingizga qulay tilni tanlang!\n-----"
                                  f"\nВыберите удобный Вам язык!", reply_markup=language_inline_button())
    else:
        action_text = B2CCommandText.objects.get(text_code=13, lang_code=user.lang).text
        message = update.message.reply_text(action_text, reply_markup=order_markup(user.lang))
        user.del_message = message.message_id
        user.save()


def main_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = B2CUser.objects.filter(telegram_id=user_id).first()
    step, created = B2CStep.objects.get_or_create(created_by=user_id)

    if user:
        if user.step.__le__(5):
            if user.step == 0:
                # ism kiritish (back)
                tex = B2CCommandText.objects.filter(text_code=2, lang_code=user.lang).first().text
                text = command_line(tex)
                update.message.delete()
                context.bot.send_message(chat_id=user_id,
                                         text=text,
                                         reply_markup=phone_keyboard(user.lang))

            elif user.step == 1:
                # wrong number or back
                tex = B2CCommandText.objects.filter(text_code=1, lang_code=user.lang).first().text
                text = command_line(tex)
                context.bot.send_message(chat_id=user_id,
                                         text=text,
                                         reply_markup=phone_keyboard(user.lang))
            elif user.step == 2:
                code = update.message.text
                check_code = checkValidMessage(user_telegram_id=user_id, code=code)
                if check_code:
                    tex = B2CCommandText.objects.filter(text_code=2, lang_code=user.lang).first().text
                    text = command_line(tex)
                    context.bot.send_message(chat_id=user_id,
                                             text=text,
                                             reply_markup=back_markup(user.lang))
                    user.step = 3
                    user.save()
                else:
                    text = B2CCommandText.objects.filter(text_code=45, lang_code=user.lang).first().text
                    context.bot.send_message(chat_id=user_id,
                                             text=text,
                                             reply_markup=phone_keyboard(user.lang))
            elif user.step == 3:
                # Tu'g'ilgan sanangizni kiriting
                name = update.message.text
                user = user_update(user_id, 'first_name', name, step=4)
                tex = B2CCommandText.objects.filter(text_code=6, lang_code=user.lang).first().text
                text = command_line(tex)
                update.message.reply_text(text, reply_markup=back_markup(user.lang))

            elif user.step == 4:
                # ro'yhatdan otildi
                data_birthday = ''
                temp = update.message.text
                numbers = [int(x) for x in re.findall(r'[+]?\d+?\d*', temp)]
                for item in numbers:
                    data_birthday += str(item.__ceil__()) + "-"
                user = user_update(user_id, 'data_birthday', data_birthday[:-1], step=5)
                text = user_profile(user_id)
                update.message.reply_text(text=text, reply_markup=sing_up_apply_markup(user.lang), parse_mode="HTML")
            elif user.step == 5:
                text = user_profile(user_id)
                update.message.reply_text(text=text, reply_markup=sing_up_apply_markup(user.lang), parse_mode="HTML")
            elif user.step == 6:
                document = open(f'media/Оферта.pdf', 'rb')
                context.bot.send_document(chat_id=user_id, filename='Оферта.pdf', document=document,
                                          reply_markup=apply_button(user.lang))
                # update.message.reply_text("Оферта", reply_markup=apply_button(user.lang))

        elif user.step == 7:
            msg = update.message.text
            chat_data = context.chat_data.get("profile", None)
            create_order_text = B2CCommandText.objects.filter(text_code=8)
            price_text = B2CCommandText.objects.filter(text_code=9)
            support_text = B2CCommandText.objects.filter(text_code=10)
            history_text = B2CCommandText.objects.filter(text_code=11)
            profile_text = B2CCommandText.objects.filter(text_code=12)
            if msg in [item.text for item in create_order_text]:
                command_warning = B2CCommandText.objects.filter(text_code=22, lang_code=user.lang).first().text
                text = command_line(command_warning)
                update.message.reply_text(text=text)
                B2CStep.objects.filter(created_by=user_id).update(is_safe=False, sender_name=user.first_name,
                                                                  from_location=user.address,
                                                                  sender_phone=user.phone_number)
                go_create_order_by_conversation(update=update, context=context)
                #  type  delivery
                # step.step = 1
                # step.save()
                # delivery_type_text = B2CCommandText.objects.get(text_code=18, lang_code=user.lang).text
                # msg = context.bot.send_message(chat_id=user.telegram_id, text=delivery_type_text,
                #                                reply_markup=type_delivery(lang_code=user.lang))
                # user.del_message = msg.message_id
                # user.save()
            elif msg in [item.text for item in history_text]:
                orders = my_orders(user.lang, user_id)
                for order in orders:
                    context.bot.send_message(chat_id=user_id, text=order, parse_mode="HTML",
                                             disable_web_page_preview=True,
                                             reply_markup=del_order_inline_button(user.lang))
            elif msg in [item.text for item in profile_text] or chat_data:
                context.chat_data['profile'] = None
                text = user_profile(user_id)
                context.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML",
                                         reply_markup=change_profile(user.lang))
            elif msg in [item.text for item in price_text]:
                document = open(f'media/costs.pdf', 'rb')
                context.bot.send_document(chat_id=user_id, filename='costs.pdf', document=document)
            elif msg in [item.text for item in support_text]:
                text = B2CCommandText.objects.get(text_code=14, lang_code=user.lang).text
                update.message.reply_text(text=text, reply_markup=order_markup(user.lang))
            elif step.step < 20:
                create_order(update, context)
            else:
                create_order_by_conversation(update, context)

        elif user.step == 8:
            msg = update.message.text
            user = user_update(user_id, 'first_name', msg, step=6)
            text = user_profile(user_id)
            context.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML",
                                     reply_markup=change_profile(user.lang))
        elif user.step == 9:
            number_tex = B2CCommandText.objects.filter(text_code=1, lang_code=user.lang).first().text
            text = command_line(number_tex)
            context.bot.send_message(chat_id=user_id, text=text,
                                     reply_markup=phone_keyboard(user.lang))
        elif user.step == 10:
            data_birthday = ''
            temp = update.message.text
            numbers = [int(x) for x in re.findall(r'[+]?\d+?\d*', temp)]
            for item in numbers:
                data_birthday += str(item.__ceil__()) + "-"
            user = user_update(user_id, 'data_birthday', data_birthday[:-1], step=6)
            text = user_profile(user_id)
            context.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML",
                                     reply_markup=change_profile(user.lang))


def accept(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = B2CUser.objects.get(telegram_id=user_id)
    if user.step.__le__(6):
        document = open(f'media/Оферта.pdf', 'rb')
        message = context.bot.send_document(chat_id=user_id, filename='Оферта.pdf', document=document,
                                            reply_markup=apply_button(user.lang))
        B2CUser.objects.filter(telegram_id=user_id).update(step=6, del_message=message.message_id)
    else:
        B2CStep.objects.filter(created_by=user_id).update(step=21)
        create_order_by_conversation(update, context)


def apply(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = B2CUser.objects.get(telegram_id=user_id)
    action_text = B2CCommandText.objects.get(text_code=13, lang_code=user.lang).text
    message = update.message.reply_text(action_text, reply_markup=order_markup(user.lang))
    B2CUser.objects.filter(telegram_id=user_id).update(is_active=True, step=7, del_message=message.message_id)


def back(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = B2CUser.objects.filter(telegram_id=user_id).first()

    if user.step == 1:
        start(update, context)
    elif user.step == 2:
        phone_wrong(update, context)
    elif user.step == 3:
        user.step = 1
        user.save()
        return main_handler(update, context)
    elif user.step == 4:
        user.step = 3
        user.save()
        return wrong_full_name(update, context)
    elif user.step == 5:
        user.step = 4
        user.save()
        return wrong_data_birthday(update, context)
        # return main_handler(update, context)
    elif user.step == 6:
        user.step = 5
        user.save()
        return main_handler(update, context)
    elif user.step == 7:
        step, created = B2CStep.objects.get_or_create(created_by=user_id)
        if step.step.__le__(11):
            step.step -= 1
            step.save()
            create_order(update, context)
        elif step.step == 21:
            B2CStep.objects.filter(created_by=user_id).update(step=0)
            update.message.delete()
            select_action_text = B2CCommandText.objects.filter(text_code=13, lang_code=user.lang).first().text
            context.bot.send_message(chat_id=user_id, text=select_action_text, reply_markup=order_markup(user.lang))
            B2CUser.objects.filter(telegram_id=user_id).update(step=6)
        elif step.step == 22:
            step.step = 21
            step.save()
            go_create_order_by_conversation(update, context)
        elif 22 < step.step < 30:
            step.step -= 2
            step.save()
            create_order_by_conversation(update, context)
    elif user.step == 9:
        user.step = 7
        user.save()
        context.chat_data['profile'] = 'profile'
        main_handler(update, context)
