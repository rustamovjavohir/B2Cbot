from django.db import transaction
from django.db.models import Q
from telegram import Update
from telegram.ext import CallbackContext

from B2CStaff.keyboards import accept_order, arrive_sender_button, get_first_image, arriva_recipient_button, \
    get_second_image, order_change_courier, courier_list_button
from B2CStaff.models import Kuryer
from B2CStaff.models import Kuryer_step
from B2CStaff.utils import inform
from tgbot.models import B2COrder, B2CPrice


@transaction.atomic
def keyboard_callback(update: Update, context: CallbackContext):
    query_data = update.callback_query.data.split('_')
    user_id = update.effective_user.id
    k_step, created = Kuryer_step.objects.get_or_create(admin_id=user_id)

    if query_data[-1].__eq__('select'):
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
                                                    parse_mode="HTML")

            msg = context.bot.send_message(text=text, chat_id=kuryer.kuryer_telegram_id, parse_mode="HTML",
                                           reply_markup=accept_order(order.id))
            order.del_message = msg.message_id
            order.save()
        else:
            update.callback_query.answer(f"Заказ №{order.id} уже выполнен")
            update.callback_query.message.edit_text(f"Заказ <strong>№{order.id}</strong> уже выполнен",
                                                    parse_mode="HTML")
    elif query_data[-1].__eq__('accept'):
        order_id = query_data[0]
        order = B2COrder.objects.filter(id=order_id).first()
        text = inform(order)
        kuryer = Kuryer.objects.get(kuryer_telegram_id=user_id)
        kuryer.status = Kuryer.StatusKuryer.COURIER_ACCEPTED_ORDER
        kuryer.save()
        order.status = B2COrder.StatusOrder.COURIER_ACCEPTED_ORDER
        # order.kuryer = kuryer
        order.save()
        update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=arrive_sender_button(order_id))
    elif query_data[-1].__eq__("came"):
        order_id = query_data[0]
        order = B2COrder.objects.filter(id=order_id).update(status=B2COrder.StatusOrder.COURIER_ARRIVED_AT_THE_SENDER)
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
        order_id = query_data[0]
        order = B2COrder.objects.filter(id=order_id).update(status=B2COrder.StatusOrder.COURIER_RECEIVED_THE_SHIPMENT)
        update.callback_query.edit_message_reply_markup(reply_markup=arriva_recipient_button(order_id))
    elif query_data[-1].__eq__("came2"):
        order_id = query_data[0]
        order = B2COrder.objects.filter(id=order_id).update(
            status=B2COrder.StatusOrder.DELIVERED)
        update.callback_query.edit_message_reply_markup(reply_markup=get_second_image(order_id))
    elif query_data[-1].__eq__("image2"):
        Kuryer.objects.filter(kuryer_telegram_id=k_step.admin_id).update(status=Kuryer.StatusKuryer.COURIER_FREE)
        order_id = query_data[0]
        k_step.step = 7
        k_step.obj = order_id
        k_step.save()
        update.callback_query.message.delete()
        context.bot.send_message(chat_id=user_id, text="📎 Сфотографируйте продукт")
