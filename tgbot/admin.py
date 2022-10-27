from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin, ImportExportModelAdmin
from import_export.formats import base_formats
from rangefilter.filters import DateRangeFilter

from B2CStaff.models import Kuryer
from .models import B2CUser, B2COrder, B2CPrice, B2CCommandText
# Register your models here.
from .resources import B2COrderResource, B2CUserResource


# admin.site.register(Order)


@admin.register(B2COrder)
class B2COrderAdmin(ImportExportActionModelAdmin, ImportExportModelAdmin):
    list_display = ["id", "order_name", "weight", "price", "status", "kuryer", "from_location",
                    "sender_name", "sender_phone", "to_location", "recipient_name", "recipient_phone", "come_back",
                    "comment", "created_at"]
    list_editable = ["comment"]
    list_display_links = ["id", "order_name", "from_location"]
    list_filter = (("created_at", DateRangeFilter), "status")
    search_fields = ["sender_name", "from_location", "order_name", "status"]
    resource_class = B2COrderResource

    def less_content(self, obj):
        return obj.content[50]

    def get_export_formats(self):
        formats = (
            base_formats.XLS,
            base_formats.XLSX,
        )
        return [f for f in formats if f().can_export()]

    def get_import_formats(self):
        formats = (
            base_formats.XLS,
            base_formats.XLSX,
        )
        return [f for f in formats if f().can_export()]


@admin.register(B2CUser)
class B2CUserAdmin(ImportExportActionModelAdmin, ImportExportModelAdmin):
    list_display = ["id", "first_name", "phone_number", "username", "address", "data_birthday", "lang"]
    # list_editable = ["address"]
    list_display_links = ["id", "first_name", "username"]
    list_filter = (("data_birthday", DateRangeFilter), "first_name", "address", "lang")
    search_fields = ["first_name", "phone_number"]
    resource_class = B2CUserResource

    def less_content(self, obj):
        return obj.content[50]

    def get_export_formats(self):
        formats = (
            base_formats.XLS,
            base_formats.XLSX,
        )
        return [f for f in formats if f().can_export()]

    def get_import_formats(self):
        formats = (
            base_formats.XLS,
            base_formats.XLSX,
        )
        return [f for f in formats if f().can_export()]


@admin.register(B2CPrice)
class B2CPriceAdmin(admin.ModelAdmin):
    list_display = ["id", "name_price_order", "price_come_back", "price", "price1", "price2", "price3",
                    "percent"]
    list_editable = ["name_price_order", "price_come_back", "price", "price1", "price2", "price3",
                     "percent"]


@admin.register(B2CCommandText)
class B2CCommandTextAdmin(admin.ModelAdmin):
    list_display = ["text", "text_code", "lang_code"]
