"""Admin Bot Admin"""

from django.contrib import admin
from .models import ServiceLocation, WeekDay


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


class WeekDayAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления днями недели.
    """

    list_display = ("__str__", "day", "start_time", "end_time")
    search_fields = ("day",)
    ordering = ("day",)


admin.site.register(ServiceLocation, ServiceLocationAdmin)
admin.site.register(WeekDay, WeekDayAdmin)
