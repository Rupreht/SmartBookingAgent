"""Bot Admin Models"""

from django.db import models
from django.utils import timezone
import datetime


class WorkDay(models.Model):
    """
    Модель для представления дня недели.
    """

    DAY_CHOICES = [
        (0, "Понедельник"),
        (1, "Вторник"),
        (2, "Среда"),
        (3, "Четверг"),
        (4, "Пятница"),
        (5, "Суббота"),
        (6, "Воскресенье"),
    ]

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
    available_days = models.ManyToManyField(WorkDay, blank=True, related_name="service_locations", verbose_name="Доступные дни недели")

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


class TelegramUser(models.Model):
    """Telegram User
    https://core.telegram.org/bots/api#chatfullinfo
    for ChatFullInfo
    """

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    username = models.CharField(max_length=32)
    bio = models.CharField(max_length=70)
    language_code = models.CharField(max_length=2)
    is_premium = models.BooleanField()
    datetime = models.DateTimeField(default=timezone.now)


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
