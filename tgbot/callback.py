import re

from telegram import Update
from telegram.ext import CallbackContext

from tgbot.keyboards import phone_keyboard, weight_type_button, locations_button, back_markup, order_markup, \
    inline, apply_button
from tgbot.models import B2CUser, B2CCommandText, B2CStep, B2COrder
from tgbot.utils import command_line, order_text, type_order_util, create_order
from tgbot.views import main_handler


def keyboard_callback(update: Update, context: CallbackContext):
    query_data = update.callback_query.data.split('-')
    user_id = update.effective_user.id
    user = B2CUser.objects.filter(telegram_id=user_id).first()
    step = B2CStep.objects.filter(created_by=user_id).first()
    if query_data[0].__eq__('lang'):
        try:
            lang = query_data[-1]
            tex = B2CCommandText.objects.filter(text_code=1, lang_code=lang).first().text
            text = command_line(tex)
            phone_text = B2CCommandText.objects.filter(text_code=3, lang_code=lang).first().text
            update.callback_query.delete_message()
            B2CUser.objects.filter(telegram_id=user_id).update(lang=lang, step=1)
            context.bot.send_message(chat_id=user_id, text="Оферта", reply_markup=apply_button(lang_code=lang))
            # context.bot.send_message(chat_id=user_id,
            #                          text=text,
            #                          reply_markup=phone_keyboard(phone_text))
        except Exception as ex:
            print(ex, "lang")
    elif query_data[0].__eq__('profile_change_name'):
        user.step = 6
        user.save()
        name_text = B2CCommandText.objects.filter(text_code=2, lang_code=user.lang).first().text
        text = command_line(name_text)
        update.callback_query.edit_message_text(text)
        # context.bot.send_message(chat_id=user_id, text=text)
    elif query_data[0].__eq__('profile_change_phone'):
        user.step = 7
        user.save()
        phone_text = B2CCommandText.objects.filter(text_code=1, lang_code=user.lang).first().text
        text = command_line(phone_text)
        update.callback_query.delete_message()
        context.bot.send_message(chat_id=user_id, text=text,
                                 reply_markup=phone_keyboard(user.lang))
    elif query_data[0].__eq__('create_order'):
        try:
            update.callback_query.message.delete()
            B2CStep.objects.filter(created_by=user_id).update(step=0)
            main_handler(update, context)
        except Exception as ex:
            print(ex)
    elif query_data[0].__eq__('simple_delivery'):
        try:
            update.callback_query.message.delete()
            B2CStep.objects.filter(created_by=user_id).update(step=1, is_safe=True)
            type_order_util(update, context)
        except Exception as ex:
            print(ex, "-simple_delivery")
    elif query_data[0].__eq__('safe_delivery'):
        try:
            update.callback_query.message.delete()
            B2CStep.objects.filter(created_by=user_id).update(step=1)
            type_order_util(update, context)
        except Exception as ex:
            print(ex, "- safe_delivery")
    elif query_data[0].__eq__('personal_order'):
        try:
            update.callback_query.message.delete()
            B2CStep.objects.filter(created_by=user_id).update(step=2, sender_name=user.first_name,
                                                              from_location=user.address,
                                                              sender_phone=user.phone_number, is_self=True)
            create_order(update, context)
        except Exception as ex:
            print(ex, '\n----Personal')
    elif query_data[0].__eq__('new_order'):
        try:
            update.callback_query.message.delete()
            B2CStep.objects.filter(created_by=user_id).update(step=2, sender_name=None,
                                                              from_location=None,
                                                              sender_phone=None,
                                                              is_self=False)
            create_order(update, context)
        except Exception as ex:
            print(ex, '\n---- new order')

    elif query_data[0].__eq__('model'):
        try:
            update.callback_query.message.delete()
        except Exception as ex:
            print(ex)
        model_name_text = B2CCommandText.objects.get(text_code=24, lang_code=user.lang).text
        msg = context.bot.send_message(chat_id=user_id, text=model_name_text,
                                       reply_markup=back_markup(user.lang))
        B2CStep.objects.filter(created_by=user_id).update(step=3, delete_message=msg.message_id)
    elif query_data[0].__eq__('weight'):
        update.callback_query.message.delete()
        model_weight_text = B2CCommandText.objects.get(text_code=25, lang_code=user.lang).text
        msg = context.bot.send_message(chat_id=user_id, text=model_weight_text,
                                       reply_markup=weight_type_button(user.lang))
        B2CStep.objects.filter(created_by=user_id).update(step=4, delete_message=msg.message_id)
    elif query_data[0].__eq__("from"):
        update.callback_query.message.delete()
        from_text = B2CCommandText.objects.get(text_code=26, lang_code=user.lang).text
        msg = context.bot.send_message(chat_id=user_id, text=from_text,
                                       reply_markup=locations_button(user.lang))
        B2CStep.objects.filter(created_by=user_id).update(step=5, delete_message=msg.message_id)
    elif query_data[0].__eq__("sender_name"):
        update.callback_query.message.delete()
        sender_name_text = B2CCommandText.objects.get(text_code=27, lang_code=user.lang).text
        msg = context.bot.send_message(chat_id=user_id, text=sender_name_text,
                                       reply_markup=back_markup(user.lang))
        B2CStep.objects.filter(created_by=user_id).update(step=6, delete_message=msg.message_id)
    elif query_data[0].__eq__("sender_phone"):
        update.callback_query.message.delete()
        sender_phone_text = B2CCommandText.objects.get(text_code=28, lang_code=user.lang).text
        msg = context.bot.send_message(chat_id=user_id, text=sender_phone_text,
                                       reply_markup=phone_keyboard(user.lang))
        B2CStep.objects.filter(created_by=user_id).update(step=7, delete_message=msg.message_id)
    elif query_data[0].__eq__("to"):
        update.callback_query.message.delete()
        to_text = B2CCommandText.objects.get(text_code=29, lang_code=user.lang).text
        msg = context.bot.send_message(chat_id=user_id, text=to_text,
                                       reply_markup=locations_button(user.lang))
        B2CStep.objects.filter(created_by=user_id).update(step=8, delete_message=msg.message_id)
    elif query_data[0].__eq__("recipient_name"):
        update.callback_query.message.delete()
        recipient_name_text = B2CCommandText.objects.get(text_code=30, lang_code=user.lang).text
        msg = context.bot.send_message(chat_id=user_id, text=recipient_name_text,
                                       reply_markup=back_markup(user.lang))
        B2CStep.objects.filter(created_by=user_id).update(step=9, delete_message=msg.message_id)
    elif query_data[0].__eq__("recipient_phone"):
        update.callback_query.message.delete()
        recipient_phone_text = B2CCommandText.objects.get(text_code=31, lang_code=user.lang).text
        msg = context.bot.send_message(chat_id=user_id, text=recipient_phone_text,
                                       reply_markup=phone_keyboard(user.lang))
        B2CStep.objects.filter(created_by=user_id).update(step=10, delete_message=msg.message_id)
    elif query_data[0].__eq__("comment"):
        update.callback_query.message.delete()
        comment_text = B2CCommandText.objects.get(text_code=32, lang_code=user.lang).text
        msg = context.bot.send_message(chat_id=user_id, text=comment_text,
                                       reply_markup=back_markup(user.lang))
        B2CStep.objects.filter(created_by=user_id).update(step=11, delete_message=msg.message_id)
    elif query_data[0].__eq__('send'):
        update.callback_query.delete_message()
        text = order_text(user.lang, user_id)
        if not step.order_name or not step.sender_name or not step.sender_phone or not step.weight or \
                not step.from_location or not step.recipient_name or not step.recipient_phone or \
                not step.to_location or step.step == 0:
            text += "\n" + B2CCommandText.objects.get(text_code=34, lang_code=user.lang).text
            context.bot.send_message(chat_id=user_id, text=text, parse_mode='HTML', reply_markup=inline(user.lang))
            B2CStep.objects.filter(created_by=user_id).update(step=12)
        else:
            text += '\nОтправился' if user.lang.__eq__("ru") else "\nYuborildi"
            B2COrder(order_name=step.order_name, weight=step.weight, sender_name=step.sender_name,
                     sender_phone=step.sender_phone, from_location=step.from_location, to_location=step.to_location,
                     recipient_name=step.recipient_name, recipient_phone=step.recipient_phone, comment=step.comment,
                     created_by=step.created_by, price=step.price, is_safe=step.is_safe).save()
            B2CUser.objects.filter(telegram_id=user_id).update(address=step.from_location)
            step.delete()
            context.bot.send_message(chat_id=user_id, text=text, parse_mode='HTML',
                                     reply_markup=order_markup(user.lang))
    elif query_data[0].__eq__('home'):
        B2CStep.objects.filter(created_by=user_id).update(step=0)
        update.callback_query.message.delete()
        context.bot.send_message(chat_id=user_id, text="Выберите действие", reply_markup=order_markup(user.lang))
        user.step = 5
        user.save()
    elif query_data[0].__eq__("order_del"):
        msg = update.callback_query.message.text
        numbers = [x for x in re.findall(r'-?\d+\.?\d*', msg)]
        if B2COrder.objects.get(id=numbers[0]).status.__eq__(B2COrder.StatusOrder.COMPLETED):
            B2COrder.objects.filter(id=numbers[0]).update(is_deleted=True)
        update.callback_query.delete_message()
    elif query_data[0].__eq__("order_close"):
        update.callback_query.delete_message()
