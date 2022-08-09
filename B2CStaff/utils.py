from B2CStaff.models import Kuryer, Dispatcher


def is_kuryer(user_id):
    has = Kuryer.objects.filter(kuryer_telegram_id=user_id).exists()
    return has


def is_disp(user_id):
    has = Dispatcher.objects.filter(dispatcher_telegram_id=user_id).exists()
    return has


def inform(order):
    text = ''
    try:
        text += f"<strong>№: </strong>{order.id}\n"
        text += f"<strong>Товар: </strong>{order.order_name}\n"
        text += f"<strong>Вес товаров: </strong>{order.weight}\n"
        if "https" in order.from_location[:10]:
            text += f"<strong>Откуда доставить: </strong> <a href='{order.from_location}'>Локация1</a>\n"
        else:
            text += f"<strong>Откуда доставить: </strong>{order.from_location}\n"
        text += f"<strong>Имя отправителя: </strong>{order.sender_name}\n"
        text += f"<strong>Номер телефон отправителя: </strong>{order.sender_phone}\n"
        if "https" in order.to_location[:10]:
            text += f"<strong>Куда доставить: </strong> <a href='{order.to_location}'>Локация2</a>\n"
        else:
            text += f"<strong>Куда доставить: </strong>{order.to_location}\n"
        text += f"<strong>Имя получателя: </strong>{order.recipient_name}\n"
        text += f"<strong>Номер телефон получателя: </strong>{order.recipient_phone}\n"
        if order.comment:
            text += f"<strong>Комментарии: </strong>{order.comment}\n"
        if order.price:
            text += f"<strong>Цена: </strong>{order.price} сум\n"
        return text
    except Exception as ex:
        print(ex)


def kuryer_text(kuryer):
    text = ""
    text += f"<strong>Курер: </strong>{kuryer.kuryer_name} \n" \
            f"<strong>Телеграм ид: </strong>{kuryer.kuryer_telegram_id}\n"
    return text
