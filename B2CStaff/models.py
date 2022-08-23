from django.db import models


class Kuryer(models.Model):
    class StatusKuryer(models.TextChoices):
        COURIER_ACCEPTED_ORDER = "Курьер принял заказ"
        COURIER_FREE = "Курьер свободен"

    kuryer_telegram_id = models.BigIntegerField(verbose_name="Курьер Telegram ID", unique=True)
    kuryer_name = models.CharField(default="", max_length=100, verbose_name="Имя курьера", blank=True)
    inwork = models.BooleanField(default=False, verbose_name="Работает?")
    status = models.CharField(max_length=250, null=True, blank=True, verbose_name="Статус")
    balance = models.IntegerField(null=True, blank=True, verbose_name="Баланс")
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата выплаты")
    ball = models.FloatField(default=5)

    def __str__(self):
        return self.kuryer_name

    class Meta:
        verbose_name = "Курьер"
        verbose_name_plural = "Курьеры"


class Dispatcher(models.Model):
    dispatcher_telegram_id = models.BigIntegerField(verbose_name="Диспетчер Telegram ID", unique=True)
    dispatcher_name = models.CharField(default="", max_length=100, verbose_name="Имя диспетчера", blank=True)

    def __str__(self):
        return self.dispatcher_name

    class Meta:
        verbose_name = "Диспетчер"
        verbose_name_plural = "Диспетчеры"


class Kuryer_step(models.Model):
    admin_id = models.BigIntegerField()
    step = models.BigIntegerField(default=0, blank=True)
    obj = models.BigIntegerField(default=0, blank=True)
