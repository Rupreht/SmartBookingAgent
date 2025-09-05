"""Admin Bot Admin"""

from django.contrib import admin
from .models import ServiceLocation, WorkDay, RentalObject, TelegramUser


class ServiceLocationAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления местами оказания услуг.
    """

    list_display = ("name", "city", "rest_of_address", "capacity", "get_working_hours")
    search_fields = ("name", "city", "rest_of_address")
    filter_horizontal = ("available_days",)
    readonly_fields = ("get_address",)

    def get_working_hours(self, obj):
        """
        Отображение графика работы в админ-панели
        """
        return obj.get_working_hours()

    get_working_hours.short_description = "График работы"

    def get_address(self, obj):
        """
        Форматированный адрес для просмотра
        """
        return obj.get_address()

    get_address.short_description = "Полный адрес"


class WorkDayAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления днями недели.
    """

    list_display = ("__str__", "day", "start_time", "end_time")
    search_fields = (
        "day",
        "start_time",
        "end_time",
    )
    ordering = ("day",)


class RentalObjectAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления объектами аренды.
    """

    list_display = ("__str__", "minimum_rental_duration")
    search_fields = ("current_location",)
    ordering = ("name", "current_location")


class TelegramUserAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления пользователями Telegram.
    """

    list_display = ("username", "first_name", "last_name", "is_premium")
    search_fields = ("username", "first_name", "last_name", "id")
    list_filter = ("is_premium",)
    readonly_fields = ("id", "datetime_joined")

    def has_add_permission(self, request):
        """Запретить добавление пользователей вручную"""
        return False


admin.site.register(ServiceLocation, ServiceLocationAdmin)
admin.site.register(WorkDay, WorkDayAdmin)
admin.site.register(RentalObject, RentalObjectAdmin)
admin.site.register(TelegramUser, TelegramUserAdmin)
