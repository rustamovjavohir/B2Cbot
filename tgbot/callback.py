import re

from telegram import Update
from telegram.ext import CallbackContext

from B2CStaff.keyboards import review_list_button
from tgbot.keyboards import phone_keyboard, weight_type_button, locations_button, back_markup, order_markup, \
    inline, apply_button, change_profile_language, change_profile, apply_get, sing_up_apply_markup
from tgbot.models import B2CUser, B2CCommandText, B2CStep, B2COrder, B2CPrice
from tgbot.utils import command_line, order_text, type_order_util, create_order, user_profile, \
    create_order_by_conversation, go_create_order_by_conversation
from tgbot.views import main_handler


def keyboard_callback(update: Update, context: CallbackContext):
    query_data = update.callback_query.data.split('-')
    user_id = update.effective_user.id
    user = B2CUser.objects.filter(telegram_id=user_id).first()
    step = B2CStep.objects.filter(created_by=user_id).first()
    if query_data[0].__eq__('lang'):
        try:
            lang = query_data[-1]
            if query_data[1].__eq__("change"):
                B2CUser.objects.filter(telegram_id=user_id).update(lang=lang)
                text = user_profile(user_id)
                update.callback_query.edit_message_text(text=text, parse_mode="HTML",
                                                        reply_markup=change_profile(lang))

            else:
                phone_text = B2CCommandText.objects.filter(text_code=3, lang_code=lang).first().text
                update.callback_query.delete_message()
                B2CUser.objects.filter(telegram_id=user_id).update(lang=lang, step=1)
                context.bot.send_message(chat_id=user_id, text=phone_text, reply_markup=phone_keyboard(lang_code=lang))
        except Exception as ex:
            print(ex, "lang")
    elif query_data[0].__eq__('profile_change_name'):
        user.step = 7
        user.save()
        name_text = B2CCommandText.objects.filter(text_code=2, lang_code=user.lang).first().text
        text = command_line(name_text)
        update.callback_query.edit_message_text(text)
    elif query_data[0].__eq__('profile_change_phone'):
        user.step = 8
        user.save()
        phone_text = B2CCommandText.objects.filter(text_code=1, lang_code=user.lang).first().text
        text = command_line(phone_text)
        update.callback_query.delete_message()
        context.bot.send_message(chat_id=user_id, text=text,
                                 reply_markup=phone_keyboard(user.lang))
    elif query_data[0].__eq__('profile_change_birthday'):
        user.step = 9
        user.save()
        birthday_text = B2CCommandText.objects.filter(text_code=6, lang_code=user.lang).first().text
        text = command_line(birthday_text)
        update.callback_query.edit_message_text(text)

    elif query_data[0].__eq__('profile_change_lang'):
        update.callback_query.edit_message_text(f"\nO'zingizga qulay tilni tanlang!\n-----"
                                                f"\nВыберите удобный Вам язык!", reply_markup=change_profile_language())

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
            B2CStep.objects.filter(created_by=user_id).update(is_safe=False, sender_name=user.first_name,
                                                              from_location=user.address,
                                                              sender_phone=user.phone_number)
            go_create_order_by_conversation(update, context)
        except Exception as ex:
            print(ex, "-simple_delivery")
    elif query_data[0].__eq__('safe_delivery'):
        try:
            update.callback_query.message.delete()
            B2CStep.objects.filter(created_by=user_id).update(step=2, is_safe=True, sender_name=user.first_name,
                                                              from_location=user.address,
                                                              sender_phone=user.phone_number)
            go_create_order_by_conversation(update, context)
        except Exception as ex:
            print(ex, "- safe_delivery")
    elif query_data[0].__eq__("edit"):
        update.callback_query.message.edit_reply_markup(reply_markup=inline(user.lang))
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
    elif query_data[0].__eq__("come_back"):
        update.callback_query.message.delete()
        b2c_step = B2CStep.objects.get(created_by=user_id)
        if b2c_step.come_back:
            b2c_step.come_back = False
            if b2c_step.is_safe:
                b2c_step.price -= B2CPrice.objects.last().price_come_back
            else:
                b2c_step.price -= B2CPrice.objects.first().price_come_back
        else:
            b2c_step.come_back = True
            if b2c_step.is_safe:
                b2c_step.price += B2CPrice.objects.last().price_come_back
            else:
                b2c_step.price += B2CPrice.objects.first().price_come_back
        b2c_step.save()
        text = order_text(user.lang, user_id)
        update.callback_query.message.reply_html(text, disable_web_page_preview=True, reply_markup=inline(user.lang))
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
            text = text.split('☝️')[0]
            text += '\nОтправился</strong>' if user.lang.__eq__("ru") else "\nYuborildi</strong>"
            B2COrder(order_name=step.order_name, weight=step.weight, sender_name=step.sender_name,
                     sender_phone=step.sender_phone, from_location=step.from_location, to_location=step.to_location,
                     recipient_name=step.recipient_name, recipient_phone=step.recipient_phone, comment=step.comment,
                     created_by=step.created_by, price=step.price, is_safe=step.is_safe,
                     come_back=step.come_back).save()
            B2CUser.objects.filter(telegram_id=user_id).update(address=step.from_location)
            step.delete()
            context.bot.send_message(chat_id=user_id, text=text, parse_mode='HTML', disable_web_page_preview=True,
                                     reply_markup=order_markup(user.lang))
    elif query_data[0].__eq__('home'):
        B2CStep.objects.filter(created_by=user_id).update(step=0)
        update.callback_query.message.delete()
        select_action_text = B2CCommandText.objects.filter(text_code=13, lang_code=user.lang).first().text
        context.bot.send_message(chat_id=user_id, text=select_action_text, reply_markup=order_markup(user.lang))
        user.step = 6
        user.save()
    elif query_data[0].__eq__("order_del"):
        msg = update.callback_query.message.text
        numbers = [x for x in re.findall(r'-?\d+\.?\d*', msg)]
        if B2COrder.objects.get(id=numbers[0]).status.__eq__(B2COrder.StatusOrder.COMPLETED):
            B2COrder.objects.filter(id=numbers[0]).update(is_deleted=True)
        update.callback_query.delete_message()
    elif query_data[0].__eq__("order_close"):
        update.callback_query.delete_message()
    elif query_data[0].__eq__("review"):
        ball = eval(query_data[-1])
        msg = update.callback_query.message
        msg = msg.text if msg.text else msg.caption
        order_id = [x for x in re.findall(r'-?\d+\.?\d*', msg)]
        kuryer = B2COrder.objects.get(id=order_id[0]).kuryer
        kuryer.ball = round((kuryer.ball + ball) / 2, 2)
        kuryer.save()
        update.callback_query.message.edit_reply_markup()
    elif query_data[-1].__eq__("apply_get_product"):
        order_id = query_data[0]
        order = B2COrder.objects.get(id=order_id)
        order.status = order.StatusOrder.COMPLETED
        order.save()
        update.callback_query.message.edit_text(text=f"№ {order_id} Mahsulot: {order.order_name}\n"
                                                     f" Xizmatga baho bering",
                                                reply_markup=review_list_button())
