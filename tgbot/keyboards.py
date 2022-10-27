from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, LoginUrl

from tgbot.models import B2CCommandText


# language_inline_button = InlineKeyboardMarkup(
#     [
#         [InlineKeyboardButton("uz", callback_data="lang-uz"), InlineKeyboardButton("ru", callback_data="lang-ru")]
#     ]
#
# )


def language_inline_button():
    button = [
        [InlineKeyboardButton("uz", callback_data="lang-uz"), InlineKeyboardButton("ru", callback_data="lang-ru")]
    ]

    return InlineKeyboardMarkup(button)


def inline(lang_code: str):
    if lang_code.__eq__("ru"):
        button = [
            [InlineKeyboardButton("Товар", callback_data="model"),
             InlineKeyboardButton("Вес товара", callback_data="weight")],
            [InlineKeyboardButton("Откуда доставить", callback_data="from"),
             InlineKeyboardButton("Имя отправителя", callback_data="sender_name"),
             InlineKeyboardButton("Номер отправителя", callback_data="sender_phone")],
            [InlineKeyboardButton("Куда доставить", callback_data="to"),
             InlineKeyboardButton("Имя получателя", callback_data="recipient_name"),
             InlineKeyboardButton("Номер получателя", callback_data="recipient_phone")],
            [InlineKeyboardButton("Комментарии", callback_data="comment"),
             InlineKeyboardButton("Обратно", callback_data="come_back")],
            [InlineKeyboardButton("📤Отправить", callback_data="send"),
             InlineKeyboardButton("🏠Главная страница", callback_data="home")]]
    else:
        button = [
            [InlineKeyboardButton("Buyum nomi", callback_data="model"),
             InlineKeyboardButton("Buyum og'irligi", callback_data="weight")],
            [InlineKeyboardButton("Qayerdan olish", callback_data="from"),
             InlineKeyboardButton("Yuboruvchining ismi", callback_data="sender_name"),
             InlineKeyboardButton("Yuboruvchining nomeri", callback_data="sender_phone")],
            [InlineKeyboardButton("Qayerga yetkazish", callback_data="to"),
             InlineKeyboardButton("Qabul qiluvchining ismi", callback_data="recipient_name"),
             InlineKeyboardButton("Qabul qiluvchining nomeri", callback_data="recipient_phone")],
            [InlineKeyboardButton("Izoh", callback_data="comment"),
             InlineKeyboardButton("Qaytib kelish", callback_data="come_back")],
            [InlineKeyboardButton("📤Jo'natish", callback_data="send"),
             InlineKeyboardButton("🏠Bosh sahifa", callback_data="home")]]
    return InlineKeyboardMarkup(button)


def back_markup(lang_code):
    back_text = B2CCommandText.objects.filter(text_code=4, lang_code=lang_code).first().text
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(back_text)]
        ],
        resize_keyboard=True, one_time_keyboard=True
    )


def edit_order_markup(lang_code):
    if lang_code.__eq__("ru"):
        button = [
            [InlineKeyboardButton("Комментарии", callback_data="comment"),
             InlineKeyboardButton("Редактировать", callback_data="edit")],
            [InlineKeyboardButton("📤Отправить", callback_data="send"),
             InlineKeyboardButton("🏠Главная страница", callback_data="home")]
        ]
    else:
        button = [
            [InlineKeyboardButton("Izoh", callback_data="comment"),
             InlineKeyboardButton("Taxrirlash", callback_data="edit")],
            [InlineKeyboardButton("📤Jo'natish", callback_data="send"),
             InlineKeyboardButton("🏠Bosh sahifa", callback_data="home")]
        ]

    return InlineKeyboardMarkup(button)


def order_markup(lang_code):
    create_order_text = B2CCommandText.objects.get(text_code=8, lang_code=lang_code).text
    price_text = B2CCommandText.objects.get(text_code=9, lang_code=lang_code).text
    support_text = B2CCommandText.objects.get(text_code=10, lang_code=lang_code).text
    history_text = B2CCommandText.objects.get(text_code=11, lang_code=lang_code).text
    profile_text = B2CCommandText.objects.get(text_code=12, lang_code=lang_code).text
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(create_order_text)],
            [
                KeyboardButton(price_text),
                KeyboardButton(support_text)
            ],
            [
                KeyboardButton(history_text),
                KeyboardButton(profile_text)
            ]
        ],
        resize_keyboard=True, one_time_keyboard=True
    )


def type_delivery(lang_code):
    simple_delivery = B2CCommandText.objects.get(text_code=19, lang_code=lang_code).text
    safe_delivery = B2CCommandText.objects.get(text_code=20, lang_code=lang_code).text
    button = [
        [InlineKeyboardButton(simple_delivery, callback_data="simple_delivery"),
         InlineKeyboardButton(safe_delivery, callback_data="safe_delivery")]
    ]
    return InlineKeyboardMarkup(button)


def type_order(lang_code):
    personal_order = B2CCommandText.objects.get(text_code=22, lang_code=lang_code).text
    new_order = B2CCommandText.objects.get(text_code=23, lang_code=lang_code).text
    button = [
        [InlineKeyboardButton(personal_order, callback_data="personal_order"),
         InlineKeyboardButton(new_order, callback_data="new_order")]
    ]
    return InlineKeyboardMarkup(button)


def profile_update(text):
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(text)]
        ], resize_keyboard=True, one_time_keyboard=True
    )


def phone_keyboard(lang_code):
    phone_text = B2CCommandText.objects.filter(text_code=3, lang_code=lang_code).first().text
    back_text = B2CCommandText.objects.filter(text_code=4, lang_code=lang_code).first().text
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(back_text), KeyboardButton(f"{phone_text}", request_contact=True)],
        ], resize_keyboard=True, one_time_keyboard=True,
    )


def locations_button(lang_code):
    back_text = B2CCommandText.objects.filter(text_code=4, lang_code=lang_code).first().text
    location_text = B2CCommandText.objects.filter(text_code=33, lang_code=lang_code).first().text
    return ReplyKeyboardMarkup(
        [[KeyboardButton(back_text),
          KeyboardButton(location_text, request_location=True)]],
        one_time_keyboard=True, resize_keyboard=True
    )


def sing_up_apply_markup(lang_code):
    back_text = B2CCommandText.objects.filter(text_code=4, lang_code=lang_code).first().text
    apply_text = B2CCommandText.objects.filter(text_code=7, lang_code=lang_code).first().text
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(back_text), KeyboardButton(apply_text)],
        ], resize_keyboard=True, one_time_keyboard=True,
    )


def apply_button(lang_code):
    back_text = B2CCommandText.objects.filter(text_code=4, lang_code=lang_code).first().text
    accept = B2CCommandText.objects.filter(text_code=5, lang_code=lang_code).first().text
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(f"{back_text}"), KeyboardButton(f"{accept}")],
        ], resize_keyboard=True, one_time_keyboard=True,
    )


def yes_or_no_button(lang_code):
    if lang_code.__eq__('ru'):
        button = [
            [KeyboardButton(f"Нет"), KeyboardButton(f"Да")]
        ]
    else:
        button = [
            [KeyboardButton(f"Yo'q"), KeyboardButton(f"Ha")]
        ]
    return ReplyKeyboardMarkup(button, resize_keyboard=True)


def weight_type_button(lang_code):
    back_text = B2CCommandText.objects.filter(text_code=4, lang_code=lang_code).first().text
    foot_courier_text = B2CCommandText.objects.filter(text_code=41, lang_code=lang_code).first().text
    driver_courier_text = B2CCommandText.objects.filter(text_code=42, lang_code=lang_code).first().text
    cargo_courier = B2CCommandText.objects.filter(text_code=43, lang_code=lang_code).first().text
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(foot_courier_text)],
            [KeyboardButton(driver_courier_text)],
            [KeyboardButton(cargo_courier)],
            [KeyboardButton(back_text)]
        ],
        one_time_keyboard=True, resize_keyboard=True)
    # return ReplyKeyboardMarkup(
    #     [[KeyboardButton("0,1 - 3 Кг"), KeyboardButton("3,1 - 6 Кг"), KeyboardButton("6,1 - 9 Кг")],
    #      [KeyboardButton("9,1 - 12 Кг"), KeyboardButton("12,1 - 15 Кг"),
    #       KeyboardButton("15,1 Кг ->")],
    #      [KeyboardButton(back_text)]],
    #     one_time_keyboard=True, resize_keyboard=True)


def change_profile(lang_code):
    edit_name_text = B2CCommandText.objects.get(text_code=15, lang_code=lang_code).text
    edit_phone_text = B2CCommandText.objects.get(text_code=16, lang_code=lang_code).text
    edit_lang_text = B2CCommandText.objects.get(text_code=38, lang_code=lang_code).text
    edit_birthday = B2CCommandText.objects.get(text_code=39, lang_code=lang_code).text
    home_text = B2CCommandText.objects.get(text_code=17, lang_code=lang_code).text
    button = [
        [InlineKeyboardButton(edit_name_text, callback_data="profile_change_name"),
         InlineKeyboardButton(edit_lang_text, callback_data="profile_change_lang")],
        [InlineKeyboardButton(edit_phone_text, callback_data="profile_change_phone"),
         InlineKeyboardButton(edit_birthday, callback_data="profile_change_birthday")],
        [InlineKeyboardButton(home_text, callback_data="home")]

    ]
    return InlineKeyboardMarkup(button)


def change_profile_language():
    button = [
        [InlineKeyboardButton("uz", callback_data="lang-change-uz"),
         InlineKeyboardButton("ru", callback_data="lang-change-ru")]
    ]

    return InlineKeyboardMarkup(button)


def del_order_inline_button(lang_code):
    close_text = B2CCommandText.objects.get(text_code=36, lang_code=lang_code).text
    delete_text = B2CCommandText.objects.get(text_code=37, lang_code=lang_code).text
    button = [
        [InlineKeyboardButton(delete_text, callback_data="order_del"),
         InlineKeyboardButton(close_text, callback_data="order_close")]
    ]
    return InlineKeyboardMarkup(button)


def apply_get(order_id):
    button = [
        [
            InlineKeyboardButton("Tasdiqlash", callback_data=f"{order_id}-apply_get_product")
        ]
    ]

    return InlineKeyboardMarkup(button)
