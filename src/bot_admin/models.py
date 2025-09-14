"""Bot Admin Models"""

import datetime
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from aiogram.utils.link import create_tg_link
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete
from django.dispatch import receiver


class WorkDay(models.Model):
    """
    Модель для представления дня недели.
    """

    DAY_CHOICES = [
        (0, _("Monday")),
        (1, _("Tuesday")),
        (2, _("Wednesday")),
        (3, _("Thursday")),
        (4, _("Friday")),
        (5, _("Saturday")),
        (6, _("Sunday")),
    ]

    SHORT_DAY_CHOICES = {
        0: _("Mon"),
        1: _("Tue"),
        2: _("Wed"),
        3: _("Thu"),
        4: _("Fri"),
        5: _("Sat"),
        6: _("Sun"),
    }

    day = models.IntegerField(choices=DAY_CHOICES, verbose_name="День недели")
    start_time = models.TimeField(auto_now=False, null=True, blank=True, verbose_name="Время начала работы")
    end_time = models.TimeField(auto_now=False, null=True, blank=True, verbose_name="Время окончания работы")

    def __str__(self):
        start = self.start_time.strftime("%H:%M") if self.start_time else "—"
        end = self.end_time.strftime("%H:%M") if self.end_time else "—"
        return f"{start}-{end} {self.get_day_display()}"

    def is_time_available(self, time: datetime.time):
        "Проверка доступности времени в рамках дня недели"
        if self.start_time and time < self.start_time:
            return False
        if self.end_time and time > self.end_time:
            return False
        return True

    def get_human_day(self):
        "возвращает полное название дня недели"
        return self.DAY_CHOICES[self.day][1]

    def get_human_short_day(self):
        "возвращает короткое название дня недели"
        return self.SHORT_DAY_CHOICES.get(self.day, "")

    class Meta:
        unique_together = ("day", "start_time", "end_time")
        verbose_name = "Рабочее время"
        verbose_name_plural = "Рабочие времена"
        ordering = ["day"]


class ServiceLocation(models.Model):
    """
    Модель для представления места оказания услуги.
    """

    # Основные поля
    name = models.CharField(max_length=255, verbose_name="Название места")
    description = models.TextField(blank=True, verbose_name="Описание места")
    city = models.CharField(max_length=255, blank=True, verbose_name="Город")
    rest_of_address = models.CharField(max_length=512, blank=True, verbose_name="Улица, дом, квартира")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Долгота")
    capacity = models.PositiveIntegerField(default=1, verbose_name="Вместимость")

    # Временные параметры
    available_days = models.ManyToManyField(
        WorkDay,
        blank=True,
        related_name="service_locations",
        verbose_name="Доступные дни недели",
    )

    class Meta:
        verbose_name = "Место оказания услуги"
        verbose_name_plural = "Места оказания услуг"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.city}"

    def is_available(self, date, time):
        """
        Проверка доступности места на указанную дату и время
        """
        weekday = date.weekday()
        if not self.available_days.exists():
            return True
        week_day = self.available_days.filter(day=weekday).first()
        if not week_day:
            return False
        return week_day.is_time_available(time)

    def get_address(self):
        """
        Форматирование полного адреса
        """
        address_parts = []
        if self.city:
            address_parts.append(self.city)
        if self.rest_of_address:
            address_parts.append(self.rest_of_address)
        address = ", ".join(address_parts)
        return address

    def get_geo(self):
        "геолокация"
        return f"{self.latitude}, {self.longitude}" if self.latitude else "-"

    def get_working_hours(self):
        """
        Получение времени работы в формате строки
        """
        hours = []
        for day in self.available_days.order_by("day").all():
            start = day.start_time.strftime("%H:%M") if day.start_time else "—"
            end = day.end_time.strftime("%H:%M") if day.end_time else "—"
            hours.append(f"{day.get_day_display()} {start}-{end}")
        return ", ".join(hours)


class RentalObject(models.Model):
    """
    Модель для объекта аренды
    """

    OBJECT_TYPES = (
        ("car", _("Car")),
        ("equipment", _("Equipment")),
        ("kite", _("Kite")),
        ("moto", _("Bike")),
        ("Spa", _("Spa")),
        ("property", _("Property")),
        ("wakeBoard", _("Wake Board")),
        ("other", _("other")),
    )

    # Основные поля
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    minimum_rental_duration = models.DurationField(
        validators=[MinValueValidator(datetime.timedelta(seconds=600))], null=False, blank=False, verbose_name="Минимальное время аренды"
    )
    type_obj = models.CharField(max_length=20, choices=OBJECT_TYPES, default="other", verbose_name="Тип объекта")
    additional_terms = models.TextField(blank=True, null=True, verbose_name="Дополнительные условия")
    current_location = models.ManyToManyField(ServiceLocation, blank=True, related_name="current_location", verbose_name="Где находится")
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)], verbose_name="Цена за день")
    is_available = models.BooleanField(default=True, verbose_name="Доступен для аренды")

    def __str__(self):
        locations = ", ".join([loc.name for loc in self.current_location.all()])
        return f"{self.name} ({locations})"

    @property
    def main_image(self):
        """Получение первого изображения для превью"""
        return self.images.first().image.url if self.images.exists() else None

    def get_image_urls(self):
        """Список URL всех изображений"""
        return [img.image.url for img in self.images.all()]

    def save(self, *args, **kwargs):
        """Валидация при сохранении объекта"""
        super().save(*args, **kwargs)

        if self.images.count() > 10:
            raise ValidationError("Максимальное количество изображений - 10")

    def short_description(self):
        """Краткое описание (первые 100 символов)"""
        return self.description[:100] + "..." if len(self.description) > 100 else self.description

    class Meta:
        verbose_name = "Объект аренды"
        verbose_name_plural = "Объекты аренды"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["type_obj", "is_available"]),
        ]


class RentalObjectImage(models.Model):
    """Модель для хранения изображений объекта аренды"""

    rental_object = models.ForeignKey(RentalObject, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(
        upload_to="rental_objects/%Y/%m/%d/",
        verbose_name="Изображение",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")

    def __str__(self):
        return f"Изображение {self.order} для {self.rental_object.name}"

    def save(self, *args, **kwargs):
        """Автоматическая нумерация изображений"""
        if not self.pk:
            last_order = (
                RentalObjectImage.objects.filter(rental_object=self.rental_object).aggregate(models.Max("order"))["order__max"] or 0
            )
            self.order = last_order + 1
        super().save(*args, **kwargs)


@receiver(post_delete, sender=RentalObjectImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)


class TelegramUser(models.Model):
    """Telegram User
    https://core.telegram.org/bots/api#user
    and
    https://docs.aiogram.dev/en/latest/_modules/aiogram/types/user.html
    and
    https://core.telegram.org/bots/api#chatfullinfo
    for ChatFullInfo
    """

    id = models.BigIntegerField(
        primary_key=True,
        help_text=_(
            """
            Unique identifier for this user or bot.
            This number may have more than 32 significant bits and some programming
            languages may have difficulty/silent defects in interpreting it.
            But it has at most 52 significant bits, so a 64-bit integer or double-precision
            float type are safe for storing this identifier."""
        ),
    )
    is_bot = models.BooleanField(help_text=_("True, if this user is a bot"))
    first_name = models.CharField(max_length=64, help_text=_("User's or bot's first name"))
    last_name = models.CharField(max_length=64, blank=True, null=True, help_text=_("Optional. User's or bot's last name"))
    username = models.CharField(max_length=32, blank=True, null=True, help_text=_("Optional. User's or bot's username"))
    language_code = models.CharField(
        max_length=15, blank=True, null=True, help_text=_("Optional. IETF language tag of the user's language")
    )
    is_premium = models.BooleanField(null=True, blank=True, help_text=_("Optional. True, if this user is a Telegram Premium user"))
    added_to_attachment_menu = models.BooleanField(
        null=True, blank=True, help_text=_("Optional. True, if this user added the bot to the attachment menu")
    )
    can_join_groups = models.BooleanField(
        null=True, blank=True, help_text=_("Optional. True, if the bot can be invited to groups. Returned only in getMe.")
    )
    can_read_all_group_messages = models.BooleanField(
        null=True, blank=True, help_text=_("Optional. True, if privacy mode is disabled for the bot. Returned only in getMe.")
    )
    supports_inline_queries = models.BooleanField(
        null=True, blank=True, help_text=_("Optional. True, if the bot supports inline queries. Returned only in getMe.")
    )
    can_connect_to_business = models.BooleanField(
        null=True,
        blank=True,
        help_text=_(
            """Optional. True, if the bot can be connected to a Telegram Business
            account to receive its messages.
            Returned only in getMe."""
        ),
    )
    has_main_web_app = models.BooleanField(
        null=True, blank=True, help_text=_("Optional. True, if the bot has a main Web App. Returned only in getMe.")
    )
    datetime_joined = models.DateTimeField(default=timezone.now)

    def full_name(self) -> str:
        "Return User Full Name"
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    def url(self) -> str:
        "Return User TG URL"
        return create_tg_link(self.username, id=self.id)


class TelegramUserProfilePhotos(models.Model):
    """Telegram User Profile Photos
    https://core.telegram.org/bots/api#userprofilephotos
    for getUserProfilePhotos
    https://core.telegram.org/bots/api#photosize
    """

    tg_user_id = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    file_id = models.CharField()
    file_unique_id = models.CharField()
    file_size = models.IntegerField()
    width = models.SmallIntegerField()
    height = models.SmallIntegerField()
    # in bytes
    file_size = models.SmallIntegerField()


class RegistrationBook(models.Model):
    "объект для регистрации бронирования"

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    rental_object = models.ForeignKey(RentalObject, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    is_confirmed = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=255, blank=True)  # ID транзакции
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Сумма оплаты
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"#{self.user.url} - {self.rental_object.name}"

    @property
    def duration_days(self):
        """Количество дней аренды"""
        delta = self.end_date - self.start_date
        return delta.days

    def calculate_total_price(self):
        """Расчёт общей стоимости"""
        return self.rental_object.price_per_day * self.duration_days

    def current_location(self) -> str:
        """Место выдачи услуги"""
        return self.rental_object.current_location

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        indexes = [
            models.Index(fields=["user", "rental_object"]),
            models.Index(fields=["start_date", "end_date"]),
            models.Index(fields=["start_datetime", "end_datetime"]),
        ]
