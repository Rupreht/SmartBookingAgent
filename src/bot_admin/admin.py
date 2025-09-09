"""Admin Bot Admin"""

from django.contrib import admin

from .models import ServiceLocation, WorkDay


@admin.register(ServiceLocation)
class ServiceLocationAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления местами оказания услуг.
    """

    list_display = ("name", "city", "rest_of_address", "capacity", "get_working_hours")
    search_fields = ("name", "city", "rest_of_address")
    filter_horizontal = ("available_days",)
    readonly_fields = ("get_address",)

    @admin.display(description="График работы")
    def get_working_hours(self, obj):
        """
        Отображение графика работы в админ-панели
        """
        return obj.get_working_hours()

    @admin.display(description="Полный адрес")
    def get_address(self, obj):
        """
        Форматированный адрес для просмотра
        """
        return obj.get_address()


@admin.register(WorkDay)
class WorkDayAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления днями недели.
    """

    list_display = ("__str__", "day", "start_time", "end_time")
    search_fields = ("day",)
    ordering = ("day",)
