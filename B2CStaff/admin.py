from django.contrib import admin

# Register your models here.
from B2CStaff.models import Kuryer, Dispatcher

admin.site.register(Dispatcher)


@admin.register(Kuryer)
class B2CKuryer(admin.ModelAdmin):
    list_display = ["kuryer_telegram_id", "kuryer_name", "status" ,"inwork", "balance",
                    "payment_date"]
    # list_editable = ["balance", "payment_date"]
    list_display_links = ["kuryer_telegram_id", "kuryer_name"]
