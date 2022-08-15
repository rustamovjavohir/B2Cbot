from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from B2CStaff.models import Kuryer


def start_button_kuryer(user_id):
    button = [[KeyboardButton("Поиск заказа")]]
    try:
        kuryer = Kuryer.objects.filter(kuryer_telegram_id=user_id).first()
    except:
        kuryer = Kuryer.objects.filter(kuryer_telegram_id=user_id).last()
    if kuryer.inwork:
        button.append([KeyboardButton("🔚Завершить работу")])
    else:
        button.append([KeyboardButton("🔛Начало работы")])
    return ReplyKeyboardMarkup(button, resize_keyboard=True, one_time_keyboard=True)


def accept_order(order_id):
    button = [
        [InlineKeyboardButton("Принять", callback_data=f"{order_id}_accept")]
    ]
    return InlineKeyboardMarkup(button)


def arrive_sender_button(order_id):
    button = [
        [InlineKeyboardButton("Я пришел", callback_data=f"{order_id}_came")]
    ]
    return InlineKeyboardMarkup(button)


def get_first_image(order_id):
    buttons = [
        [InlineKeyboardButton("📸 Сфотографировать", callback_data=f"{order_id}_image1")]
    ]
    return InlineKeyboardMarkup(buttons)


def get_second_image(order_id):
    buttons = [
        [InlineKeyboardButton("📸 Сфотографировать", callback_data=f"{order_id}_image2")]
    ]
    return InlineKeyboardMarkup(buttons)


def get_order_button(order_id):
    buttons = [
        [InlineKeyboardButton("Я отправился", callback_data=f"{order_id}_go")]
    ]
    return InlineKeyboardMarkup(buttons)


def arriva_recipient_button(order_id):
    button = [
        [InlineKeyboardButton("✅Я доставил товар получателю", callback_data=f"{order_id}_came2")]
    ]
    return InlineKeyboardMarkup(button)


def courier_start_work_button():
    button = [
        [KeyboardButton("🏠Главный страница")],
    ]
    return ReplyKeyboardMarkup(button, resize_keyboard=True, one_time_keyboard=True)


def courier_finished_work_button():
    button = [
        [KeyboardButton("✅Подтверждение")],
        [KeyboardButton("🏠Главный страница")]
    ]
    return ReplyKeyboardMarkup(button, resize_keyboard=True, one_time_keyboard=True)


def order_change_courier(order_id):
    button = [
        [InlineKeyboardButton("🔀Переназначить курьера",
                              callback_data=f"{order_id}_select")],
        [InlineKeyboardButton("❌Отменить заказ",
                              callback_data=f"{order_id}_cancelapply")]]
    return InlineKeyboardMarkup(button)


def courier_list_button(couriers, instance):
    button = []
    for i in range(1, len(couriers), 2):
        if len(couriers) > 1:
            button.append({InlineKeyboardButton(f"{couriers[i - 1].kuryer_name}",
                                                callback_data=f"{instance.id}_{couriers[i - 1].id}_kuryer"),
                           InlineKeyboardButton(f"{couriers[i].kuryer_name}",
                                                callback_data=f"{instance.id}_{couriers[i].id}_kuryer")})
    if len(couriers) % 2 == 1:
        button.append([InlineKeyboardButton(f"{couriers[len(couriers) - 1].kuryer_name}",
                                            callback_data=f"{instance.id}_{couriers[len(couriers) - 1].id}_kuryer")])

    button.append([InlineKeyboardButton(f"❌Отменить заказ",
                                        callback_data=f"{instance.id}_cancelapply")])
    return InlineKeyboardMarkup(button)


def review_list_button():
    button = [
        [
            InlineKeyboardButton("😠", callback_data='review-1'),
            InlineKeyboardButton("☹", callback_data='review-2'),
            InlineKeyboardButton("😐", callback_data='review-3'),
            InlineKeyboardButton("🙂", callback_data='review-4'),
            InlineKeyboardButton("😁", callback_data='review-5'),
        ]
    ]

    return InlineKeyboardMarkup(button)


def come_back_button(order_id):
    button = [
        [
            InlineKeyboardButton("Возвращаться", callback_data=f"{order_id}_come-back")
        ]
    ]

    return InlineKeyboardMarkup(button)


def come_back_done_button(order_id):
    button = [
        [
            InlineKeyboardButton("Вернулся", callback_data=f"{order_id}_come-back-done")
        ]
    ]

    return InlineKeyboardMarkup(button)
