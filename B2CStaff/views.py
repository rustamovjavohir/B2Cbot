import requests
from django.conf import settings
from telegram import Update, Bot
from telegram.ext import CallbackContext

from B2CStaff.keyboards import start_button_kuryer, get_order_button, courier_start_work_button, \
    courier_finished_work_button, accept_order, arriva_recipient_button
from B2CStaff.models import Kuryer_step, Dispatcher, Kuryer
from B2CStaff.utils import is_kuryer, is_disp, inform
from tgbot.models import B2COrder, B2CCommandText, B2CUser

b2cbot = Bot(token=settings.TELEGRAM_TOKEN)


def start(update: Update, context: CallbackContext):
    try:
        user_id = update.message.from_user.id
        if is_kuryer(user_id):
            update.message.delete()
            update.message.reply_text(
                f"<i>Ассалому алейкум! <ins><b>{update.message.from_user.first_name}</b></ins></i>\n"
                f"<i>Роль: <ins><b>Курьер</b></ins></i>",
                reply_markup=start_button_kuryer(user_id), parse_mode="HTML")
        elif is_disp(user_id):
            update.message.delete()

            update.message.reply_text(
                f"<i>Ассалому алейкум! <ins><b>{update.message.from_user.first_name}</b></ins></i>\n"
                f"<i>Роль: <ins><b>Диспетчер</b></ins></i>",
                parse_mode="HTML", )

        else:
            update.message.delete()
            update.message.reply_text(f"ID: {user_id}")
    except:
        pass


def kuryer_handler(update: Update, context: CallbackContext):
    dispatchers = Dispatcher.objects.all()
    photo = update.message.photo
    msg = update.message.text
    user_id = update.effective_user.id
    k_step = Kuryer_step.objects.get(admin_id=user_id)

    if k_step.step == 0 and msg == "Поиск заказа":
        update.message.delete()
        Kuryer_step.objects.filter(admin_id=user_id).update(step=1)
        update.message.reply_text("Введите номер заказа",
                                  reply_markup=courier_start_work_button())
    elif k_step.step == 1 and msg != "🏠Главный страница":
        try:
            order = B2COrder.objects.get(pk=msg)
            kuryer = Kuryer.objects.filter(kuryer_name=order.kuryer).first()
            if str(kuryer.kuryer_telegram_id) == str(user_id):
                if order.status == B2COrder.StatusOrder.COURIER_ACCEPTED_ORDER or \
                        order.status == B2COrder.StatusOrder.DELIVERED:

                    update.message.reply_text(parse_mode="HTML",
                                              disable_web_page_preview=True,
                                              text=inform(order), reply_markup=accept_order(order.id))
                elif order.status == B2COrder.StatusOrder.DELIVERY_OF_PAYMENT_OR_DOCUMENT_TO_PARTNER:
                    update.message.reply_text(parse_mode="HTML",
                                              disable_web_page_preview=True,
                                              text=inform(order), reply_markup=arriva_recipient_button(order.id))
                else:
                    update.message.reply_text("🔴Этот заказ завершен")
            else:
                update.message.reply_text("Этот заказ был передан другому курьеру")
        except:
            update.message.reply_text("🤷‍♂️На этот номер нет заказа")

    elif k_step.step == 0 and msg == "🔛Начало работы":
        update.message.delete()
        Kuryer_step.objects.filter(admin_id=user_id).update(step=2)
        update.message.reply_text("📎 Сделайте селфи внешнего вида",
                                  reply_markup=courier_start_work_button())
    elif k_step.step == 2 and len(photo) > 0:
        update.message.delete()
        try:
            kuryer = Kuryer.objects.get(kuryer_telegram_id=user_id)
        except:
            kuryer = Kuryer.objects.filter(kuryer_telegram_id=user_id)[0]
        # group = Kuryer_came_group.objects.all()
        # for i in group:
        #     try:
        #         context.bot.send_photo(chat_id=i.kuryer_id, photo=photo[-1].file_id,
        #                                caption=f"Курьер: {kuryer.kuryer_name}\nКурьер начал работу")
        #     except:
        #         pass

        for dispatcher in dispatchers:
            context.bot.send_photo(chat_id=dispatcher.dispatcher_telegram_id, photo=photo[-1].file_id,
                                   caption=f"Курьер: {kuryer.kuryer_name}\nКурьер начал работу")
        Kuryer_step.objects.filter(admin_id=user_id).update(step=0)
        Kuryer.objects.filter(kuryer_telegram_id=user_id).update(inwork=True)
        update.message.reply_text(reply_markup=start_button_kuryer(user_id), text="😊Удачи в работе, не уставай")
    elif k_step.step == 0 and msg == "🔚Завершить работу":
        update.message.delete()
        Kuryer_step.objects.filter(admin_id=user_id).update(step=3)
        update.message.reply_text("Вы подтверждаете, что выполнили свою работу?",
                                  reply_markup=courier_finished_work_button())
    elif k_step.step == 3 and msg == "✅Подтверждение":
        update.message.delete()
        Kuryer_step.objects.filter(admin_id=user_id).update(step=0)
        Kuryer.objects.filter(kuryer_telegram_id=user_id).update(inwork=False)
        update.message.reply_text(reply_markup=start_button_kuryer(user_id), text="🥱Хорошего отдыха до завтра")
    elif msg == "🏠Главный страница":
        update.message.delete()
        Kuryer_step.objects.filter(admin_id=user_id).update(step=0)
        update.message.reply_text(reply_markup=start_button_kuryer(user_id), text="<i>Главный страница</i>",
                                  parse_mode="HTML")
    elif k_step.step == 4:
        if photo:
            B2COrder.objects.filter(pk=k_step.obj).update(before_image=photo[-1].file_id)
            obj = B2COrder.objects.get(pk=k_step.obj)
            update.message.delete()

            update.message.reply_photo(photo=obj.before_image, caption=inform(obj),
                                       reply_markup=get_order_button(order_id=obj.id), parse_mode="HTML",
                                       )
            for dispatcher in dispatchers:
                context.bot.send_photo(chat_id=dispatcher.dispatcher_telegram_id,
                                       photo=obj.before_image, parse_mode="HTML",
                                       caption=f"✅№{obj.id} Курьер получил заказ \nТовар: {obj.order_name}")

            Kuryer_step.objects.filter(admin_id=user_id).update(step=0)
        else:
            update.message.delete()
            update.message.reply_text("❗️❗️❗️🤨  Только фото")

    elif k_step.step == 7:
        if photo:
            B2COrder.objects.filter(pk=k_step.obj).update(after_image=photo[-1].file_id,
                                                          status=B2COrder.StatusOrder.COMPLETED)
            obj = B2COrder.objects.get(pk=k_step.obj)
            update.message.delete()

            update.message.reply_photo(photo=obj.before_image)
            update.message.reply_photo(photo=obj.after_image, caption=inform(obj), parse_mode="HTML",
                                       )
            file_path2 = context.bot.getFile(obj.after_image).file_path
            response = requests.get(file_path2)

            order_owner = B2CUser.objects.get(telegram_id=obj.created_by)
            order_has_been_delivered = B2CCommandText.objects.get(text_code=35, lang_code=order_owner.lang).text
            order = "Товар" if order_owner.lang.__eq__("ru") else "Mahsulot"
            b2cbot.send_photo(chat_id=obj.created_by,
                              photo=response.content, parse_mode="HTML",
                              caption=f"✅№ {obj.id} {order_has_been_delivered}\n{order}: {obj.order_name}")

            Kuryer_step.objects.filter(admin_id=user_id).update(step=0)
        else:
            update.message.delete()
            update.message.reply_text("❗️❗️❗️🤨  Только фото")


def main_handler(update: Update, context: CallbackContext):
    kuryer_handler(update, context)
