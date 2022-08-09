from import_export import resources
from import_export.fields import Field

from .models import B2COrder, B2CUser, B2CPrice


class B2COrderResource(resources.ModelResource):
    id = Field(attribute="id", column_name="НОМЕР ЗАКАЗ")
    order_name = Field(attribute="order_name", column_name="Наименование товара")
    weight = Field(attribute="weight", column_name="Вес товара")
    from_location = Field(attribute="from_location", column_name="Откуда забрать")
    sender_name = Field(attribute="sender_name", column_name="Имя отправителя")
    sender_phone = Field(attribute="sender_phone", column_name="Номер отправителя")
    to_location = Field(attribute="to_location", column_name="Куда доставить")
    recipient_name = Field(attribute="recipient_name", column_name="Имя получателя")
    recipient_phone = Field(attribute="recipient_phone", column_name="Номер получателя")
    comment = Field(attribute="comment", column_name="Комментарии")
    status = Field(attribute="status", column_name="Статус")
    created_at = Field(attribute="created_at", column_name="Дата")
    # kuryer = Field(attribute="kuryer", column_name="Курьер")
    # dis_comment = Field(attribute="dis_comment", column_name="Примечание")

    class Meta:
        model = B2COrder
        ordering = ["id"]


class B2CUserResource(resources.ModelResource):
    id = Field(attribute="id",  column_name="№: ID")
    first_name = Field(attribute="first_name", column_name="Имя Пользователи")
    phone_number = Field(attribute="phone_number", column_name="Номер Пользователи")
    username = Field(attribute="username", column_name="Телеграм профил")
    address = Field(attribute="address", column_name="Адрес")
    data_birthday = Field(attribute="data_birthday", column_name="Дата рождения")
    lang = Field(attribute="lang", column_name="Язык")

    class Meta:
        model = B2CUser
        ordering = ["id"]


class B2CPriceResource(resources.ModelResource):
    id = Field(attribute="id", column_name="№")
    name_price_order = Field(attribute="name_price_order", column_name="Тип доставки")
    price = Field(attribute="price", column_name="Цена")
    price1 = Field(attribute="price1", column_name="Цена (0-3Кг)")
    price2 = Field(attribute="price2", column_name="Цена (3-6Кг)")
    price3 = Field(attribute="price3", column_name="Цена (6-9Кг)")
    price4 = Field(attribute="price4", column_name="Цена (9-12Кг)")
    price5 = Field(attribute="price5", column_name="Цена (12-15Кг)")
    price6 = Field(attribute="price6", column_name="Цена (12 Кг ->)")

    class Meta:
        model = B2CPrice
        ordering = ["id"]
