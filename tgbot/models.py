from django.db import models

# Create your models here.
from B2CStaff.models import Kuryer


class B2CUser(models.Model):
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True, verbose_name="Телеграм ид")
    username = models.CharField(max_length=250, verbose_name="Телеграм профил")
    first_name = models.CharField(max_length=250, null=True, blank=True, verbose_name="Имя Пользователя")
    last_name = models.CharField(max_length=250, null=True, blank=True, verbose_name="Фамилия Пользователя")
    full_name = models.CharField(max_length=250, verbose_name="Имя Пользователя")
    phone_number = models.CharField(max_length=13, null=True, blank=True, verbose_name="Номер Пользователя")
    data_birthday = models.CharField(max_length=25, null=True, blank=True, verbose_name="Дата рождения")
    image = models.ImageField(upload_to='user', null=True, blank=True)
    step = models.IntegerField(default=0)
    del_message = models.IntegerField(null=True, blank=True)
    lang = models.CharField(max_length=5, default='uz')
    address = models.CharField(max_length=4096, null=True, blank=True, verbose_name="Адрес")
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']
        verbose_name = 'Б2С Пользовател'
        verbose_name_plural = 'Б2С Пользователи'

    def __str__(self):
        return self.username


class B2CCommandText(models.Model):
    text = models.TextField()
    text_code = models.IntegerField()
    lang_code = models.CharField(max_length=5)

    class Meta:
        ordering = ['text_code']
        verbose_name = 'Текст команды'
        verbose_name_plural = 'Текст команды'

    def __str__(self):
        return self.text


class B2COrder(models.Model):
    class StatusOrder(models.TextChoices):
        ORDER_PROCESSED = "Заказ оформлен"
        ORDER_CANCELLED = "Заказ отменен"
        COURIER_APPOINTED = "Курьер назначен"
        COURIER_ACCEPTED_ORDER = "Курьер принял заказ"
        COURIER_ARRIVED_AT_THE_SENDER = "Курьер приехал к отправителю"
        COURIER_RECEIVED_THE_SHIPMENT = "Курьер получил заказ"
        DELIVERED = "Доставляется"
        COURIER_ARRIVED_AT_THE_RECIPIENT = "Курьер приехал к получателю"
        ORDER_COME_BACK = "Товар возвращаться"
        CUSTOMER_CONFIRMATION_PENDING = "Ожидается подтверждение клиента"
        COMPLETED = '✅Завершен'

    order_name = models.CharField(max_length=2000, verbose_name="Наименование товара")
    weight = models.CharField(max_length=250, verbose_name="Вес товара")
    from_location = models.CharField(max_length=2000, verbose_name="Откуда забрать")
    sender_name = models.CharField(max_length=250, verbose_name="Имя отправителя")
    sender_phone = models.CharField(max_length=13, verbose_name="Номер отправителя")
    to_location = models.CharField(max_length=250, verbose_name="Куда доставить")
    recipient_name = models.CharField(max_length=250, verbose_name="Имя получателя")
    recipient_phone = models.CharField(max_length=13, verbose_name="Номер получателя")
    comment = models.CharField(max_length=2000, null=True, blank=True, verbose_name="Комментарии")
    status = models.CharField(default="Заказ оформлен", max_length=250, null=True, blank=True, verbose_name="Статус")
    price = models.IntegerField(null=True, blank=True, verbose_name="Цена")
    kuryer = models.ForeignKey(Kuryer, on_delete=models.SET_NULL, null=True, blank=True)
    is_safe = models.BooleanField(default=False, verbose_name="Безопасно")
    before_image = models.CharField(default="", max_length=150, verbose_name="Первая картинка", blank=True)
    after_image = models.CharField(default="", max_length=150, verbose_name="Вторая картинка", blank=True)
    created_by = models.BigIntegerField()
    come_back = models.BooleanField(default=False, verbose_name="Обратно")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    delivery_done_time = models.CharField(null=True, max_length=20, verbose_name="Время завершение доставки")
    del_message = models.IntegerField(null=True, blank=True)
    del_courier = models.IntegerField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Б2С Заказ'
        verbose_name_plural = 'Б2С Заказы'

    def __str__(self):
        return self.order_name


class B2CStep(models.Model):
    created_by = models.BigIntegerField(null=True, blank=True)
    order_name = models.CharField(max_length=2000, null=True, blank=True)
    weight = models.CharField(max_length=250, null=True, blank=True)
    from_location = models.CharField(max_length=2000, null=True, blank=True)
    sender_name = models.CharField(max_length=250, null=True, blank=True)
    sender_phone = models.CharField(max_length=13, null=True, blank=True)
    to_location = models.CharField(max_length=250, null=True, blank=True)
    recipient_name = models.CharField(max_length=250, null=True, blank=True)
    recipient_phone = models.CharField(max_length=13, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True, verbose_name="Цена")
    step = models.IntegerField(default=0)
    is_self = models.BooleanField(default=True)
    is_safe = models.BooleanField(default=False)
    come_back = models.BooleanField(default=False)
    delete_message = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.order_name


class B2CPrice(models.Model):
    name_price_order = models.CharField(max_length=250, verbose_name="Тип доставки")
    price = models.IntegerField(null=True, blank=True, verbose_name="Цена")
    price1 = models.IntegerField(null=True, blank=True, verbose_name="Цена (0-3Кг)")
    price2 = models.IntegerField(null=True, blank=True, verbose_name="Цена (3-6Кг)")
    price3 = models.IntegerField(null=True, blank=True, verbose_name="Цена (6-9Кг)")
    price4 = models.IntegerField(null=True, blank=True, verbose_name="Цена (9-12Кг)")
    price5 = models.IntegerField(null=True, blank=True, verbose_name="Цена (12-15Кг)")
    price6 = models.IntegerField(null=True, blank=True, verbose_name="Цена (12 Кг ->)")
    percent = models.IntegerField(null=True, blank=True, verbose_name="Процент (%)")
    price_come_back = models.IntegerField(null=True, blank=True, verbose_name="Цена Обратно")

    class Meta:
        ordering = ["id"]
        verbose_name = 'Б2С Настройки цена'
        verbose_name_plural = 'Б2С Настройки цены'

    def __str__(self):
        return self.name_price_order
