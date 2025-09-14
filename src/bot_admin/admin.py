"""Admin Bot Admin"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import ServiceLocation, WorkDay, RentalObject, TelegramUser, RegistrationBook, RentalObjectImage


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
    search_fields = (
        "day",
        "start_time",
        "end_time",
    )
    ordering = ("day",)


class RentalObjectImageInline(admin.TabularInline):
    """Инлайн для добавления изображений к объекту аренды"""

    model = RentalObjectImage
    extra = 1
    max_num = 10  # Максимальное общее количество изображений
    fields = ("image", "order", "image_preview")
    readonly_fields = ("image_preview",)
    verbose_name = _("Изображение")
    verbose_name_plural = _("Изображения объекта")

    @admin.display(description=_("Превью"))
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.image.url)
        return _("Нет изображения")

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj is not None:
            # Получаем текущее количество изображений для объекта аренды
            current_count = obj.images.count()
            # Если количество изображений достигло 10, устанавливаем extra = 0
            if current_count >= 10:
                formset.extra = 0
        return formset


@admin.register(RentalObject)
class RentalObjectAdmin(admin.ModelAdmin):
    list_display = ("name", "type_obj", "price_per_day", "is_available", "main_image_preview")
    list_filter = ("type_obj", "is_available")
    search_fields = ("name", "description")
    filter_horizontal = ("current_location",)
    inlines = [RentalObjectImageInline]
    fieldsets = (
        (None, {"fields": ("name", "type_obj", "description")}),
        (_("Условия аренды"), {"fields": ("minimum_rental_duration", "price_per_day", "additional_terms")}),
        (_("Локация и доступность"), {"fields": ("current_location", "is_available")}),
    )

    @admin.display(description=_("Главное изображение"))
    def main_image_preview(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.main_image)
        return _("Нет изображения")

    @admin.display(description=_("Краткое описание"))
    def short_description(self, obj):
        return obj.description[:100] + "..." if len(obj.description) > 100 else obj.description

    def save_formset(self, request, form, formset, change):
        """Валидация количества изображений при сохранении"""
        instances = formset.save(commit=False)
        if len(instances) + form.instance.images.count() > 10:
            raise ValidationError(_("Максимальное количество изображений - 10"))
        super().save_formset(request, form, formset, change)


@admin.register(RentalObjectImage)
class RentalObjectImageAdmin(admin.ModelAdmin):
    list_display = ("rental_object_link", "order", "image_preview")
    list_editable = ("order",)
    list_filter = ("rental_object__type_obj",)
    search_fields = ("rental_object__name",)
    ordering = ("rental_object", "order")

    @admin.display(description=_("Объект аренды"))
    def rental_object_link(self, obj):
        url = reverse("admin:bot_admin_rentalobject_change", args=[obj.rental_object.id])
        return format_html('<a href="{}">{}</a>', url, obj.rental_object.name)

    @admin.display(description=_("Превью"))
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.image.url)
        return _("Нет изображения")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("rental_object")


@admin.register(RegistrationBook)
class RegistrationBookAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для управления объектами аренды.
    """

    list_display = ("__str__", "start_datetime", "end_datetime")
    search_fields = ("current_location",)
    ordering = ("start_date",)


@admin.register(TelegramUser)
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
