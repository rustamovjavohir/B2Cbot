from django.db import transaction
from django.db.models import Q
from telegram import Update
from telegram.ext import CallbackContext

from B2CStaff.keyboards import accept_order, arrive_sender_button, get_first_image, arriva_recipient_button, \
    get_second_image, order_change_courier, courier_list_button, come_back_done_button, order_canceled_button, \
    kuryers_list_button
from B2CStaff.models import Kuryer
from B2CStaff.models import Kuryer_step
from B2CStaff.utils import inform, calendarCustom
from tgbot.models import B2COrder, B2CPrice


@transaction.atomic
def keyboard_callback(update: Update, context: CallbackContext):
    query_data = update.callback_query.data.split('_')
    user_id = update.effective_user.id
    k_step, created = Kuryer_step.objects.get_or_create(admin_id=user_id)
    if query_data[0].__eq__('cbcal'):
        date = calendarCustom(update=update, context=context, callback=update.callback_query)
        print(date)
    elif query_data[-1].__eq__('select'):
        courier = Kuryer.objects.filter(inwork=True, balance__gte=1).filter(
            ~Q(status=Kuryer.StatusKuryer.COURIER_ACCEPTED_ORDER))
        order_id = query_data[0]
        order = B2COrder.objects.get(id=order_id)
        try:
            context.bot.delete_message(chat_id=order.kuryer.kuryer_telegram_id, message_id=order.del_message)
        except Exception as ex:
            print(ex)
        update.callback_query.edit_message_reply_markup(reply_markup=courier_list_button(courier, instance=order))

    elif query_data[-1].__eq__('kuryer'):
        kur_id = query_data[-2]
        order_id = query_data[0]
        order = B2COrder.objects.filter(id=order_id).first()
        kuryer = Kuryer.objects.filter(pk=kur_id).first()
        if order.status == order.StatusOrder.COURIER_APPOINTED or \
                order.status == order.StatusOrder.COURIER_ACCEPTED_ORDER or \
                order.status == order.StatusOrder.ORDER_PROCESSED:
            order.status = B2COrder.StatusOrder.COURIER_APPOINTED
            order.kuryer = kuryer
            order.save()
            text = inform(order)
            update.callback_query.edit_message_text(text=text, reply_markup=order_change_courier(order_id),
                                                    disable_web_page_preview=True, parse_mode="HTML")

            msg = context.bot.send_message(text=text, chat_id=kuryer.kuryer_telegram_id, parse_mode="HTML",
                                           disable_web_page_preview=True, reply_markup=accept_order(order.id))

            order.del_message = msg.message_id
            order.save()
        else:
            update.callback_query.answer(f"Заказ №{order.id} уже выполнен")
            update.callback_query.message.edit_text(f"Заказ <strong>№{order.id}</strong> уже выполнен",
                                                    parse_mode="HTML")
    elif query_data[-1].__eq__("cancelapply"):
        order_id = query_data[0]
        order = B2COrder.objects.get(pk=order_id)
        new_text = update.callback_query.message.text + f'\n\n<strong>Курьер:</strong> {order.kuryer} \n' \
                                                        f'Вы действительно хотите отменить заказ? 👇'
        update.callback_query.message.edit_text(
            text=new_text,
            parse_mode="HTML", disable_web_page_preview=True,
            reply_markup=order_canceled_button(order_id))
    elif query_data[-1].__eq__("keep"):
        order_id = query_data[0]
        order = B2COrder.objects.get(pk=order_id)
        kuryer = Kuryer.objects.filter(inwork=True, balance__gte=1).filter(
            ~Q(status=Kuryer.StatusKuryer.COURIER_ACCEPTED_ORDER))
        text = inform(order)
        update.callback_query.message.edit_text(
            text=text,
            parse_mode="HTML", disable_web_page_preview=True,
            reply_markup=kuryers_list_button(kuryer, order_id))
    elif query_data[-1].__eq__("cancel"):
        order_id = query_data[0]
        order = B2COrder.objects.get(pk=order_id)
        if order.status in [order.StatusOrder.ORDER_PROCESSED, order.StatusOrder.COURIER_APPOINTED,
                            order.StatusOrder.COURIER_ACCEPTED_ORDER]:

            order.status = order.StatusOrder.ORDER_CANCELLED
            order.save()
            kuryer = Kuryer_step.objects.filter(obj=order_id).first()
            Kuryer.objects.filter(kuryer_telegram_id=kuryer.admin_id).update(status=Kuryer.StatusKuryer.COURIER_FREE)
            new_text = inform(order)
            try:
                if order.kuryer:
                    kuryer_id = order.kuryer.kuryer_telegram_id
                    context.bot.edit_message_text(chat_id=kuryer_id, message_id=order.del_message, parse_mode="HTML",
                                                  text=f"Заказ <strong>№{order_id}</strong> был ❌отменен диспетчером")
                update.callback_query.message.edit_text(text=new_text + "\n❌Заказ отменен", parse_mode="HTML",
                                                        disable_web_page_preview=True)
            except Exception as ex:
                print(ex)
        else:
            update.callback_query.answer(f"Заказ №{order.id}\n"
                                         f"Статус {order.status}")
    elif query_data[-1].__eq__('accept'):
        order_id = query_data[0]
        order = B2COrder.objects.filter(id=order_id).first()
        text = inform(order)
        kuryer = Kuryer.objects.get(kuryer_telegram_id=user_id)
        kuryer.status = Kuryer.StatusKuryer.COURIER_ACCEPTED_ORDER
        kuryer.save()
        order.status = B2COrder.StatusOrder.COURIER_ACCEPTED_ORDER
        Kuryer_step.objects.filter(admin_id=kuryer.kuryer_telegram_id).update(obj=order_id)
        # order.kuryer = kuryer
        order.save()
        update.callback_query.edit_message_text(text, parse_mode="HTML", disable_web_page_preview=True,
                                                reply_markup=arrive_sender_button(order_id))
    elif query_data[-1].__eq__("came"):
        order_id = query_data[0]
        order = B2COrder.objects.get(id=order_id)
        order.status = B2COrder.StatusOrder.COURIER_ARRIVED_AT_THE_SENDER
        order.save()
        update.callback_query.edit_message_reply_markup(reply_markup=get_first_image(order_id))
    elif query_data[-1].__eq__("image1"):
        order_id = query_data[0]
        order = B2COrder.objects.get(id=order_id)
        kuryer = Kuryer.objects.get(kuryer_telegram_id=user_id)
        if order.is_safe:
            percent = B2CPrice.objects.all()[1].percent
        else:
            percent = B2CPrice.objects.all()[0].percent
        kuryer.balance -= order.price * percent / 100
        kuryer.save()
        k_step.step = 4
        k_step.obj = order_id
        k_step.save()
        update.callback_query.message.delete()
        context.bot.send_message(chat_id=user_id, text="📎 Сфотографируйте продукт")
    elif query_data[-1].__eq__("go"):
        order_id = query_data[0]  # go
        order = B2COrder.objects.get(id=order_id)
        order.status = B2COrder.StatusOrder.DELIVERED
        order.save()
        update.callback_query.edit_message_reply_markup(reply_markup=arriva_recipient_button(order_id))
    elif query_data[-1].__eq__("came2"):
        order_id = query_data[0]
        order = B2COrder.objects.get(id=order_id)
        order.status = B2COrder.StatusOrder.COURIER_ARRIVED_AT_THE_RECIPIENT
        order.save()
        update.callback_query.edit_message_reply_markup(reply_markup=get_second_image(order_id))
    elif query_data[-1].__eq__("image2"):
        Kuryer.objects.filter(kuryer_telegram_id=k_step.admin_id).update(status=Kuryer.StatusKuryer.COURIER_FREE)
        order_id = query_data[0]
        k_step.step = 7
        k_step.obj = order_id
        k_step.save()
        update.callback_query.message.delete()
        context.bot.send_message(chat_id=user_id, text="📎 Сфотографируйте продукт")
    elif query_data[-1].__eq__("come-back"):
        order_id = query_data[0]
        msg = update.callback_query.edit_message_reply_markup(reply_markup=come_back_done_button(order_id))
        order = B2COrder.objects.get(id=order_id)
        order.status = order.StatusOrder.ORDER_COME_BACK
        order.del_message = msg.message_id
        order.save()
    elif query_data[-1].__eq__("come-back-done"):
        order_id = query_data[0]
        order = B2COrder.objects.get(id=order_id)
        order.status = order.StatusOrder.CUSTOMER_CONFIRMATION_PENDING
        order.save()
        update.callback_query.edit_message_reply_markup()
