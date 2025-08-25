"Загружает в базу популярное расписание рабочего времени"

from django.core.management.base import BaseCommand
from bot_admin.models import WorkDay


class Command(BaseCommand):
    "Класс для создания в manage под-команды"

    help = "Заполняет модель WorkDay данными о рабочих днях"
    output_transaction = True
    requires_migrations_checks = True

    def handle(self, *args, **kwargs):
        self.populate_work_days()

    def populate_work_days(self):
        "Заполняет модель WorkDay данными о рабочих днях"
        days = [
            (0, "09:00", "18:00"),  # Понедельник
            (1, "09:00", "18:00"),  # Вторник
            (2, "09:00", "18:00"),  # Среда
            (3, "09:00", "18:00"),  # Четверг
            (4, "09:00", "18:00"),  # Пятница
            (5, "09:00", "18:00"),  # Суббота
            (6, "09:00", "18:00"),  # Воскресенье
            (0, "10:00", "19:00"),  # Понедельник
            (1, "10:00", "19:00"),  # Вторник
            (2, "10:00", "19:00"),  # Среда
            (3, "10:00", "19:00"),  # Четверг
            (4, "10:00", "19:00"),  # Пятница
            (5, "10:00", "19:00"),  # Суббота
            (6, "10:00", "19:00"),  # Воскресенье
            (0, "09:00", "21:00"),  # Понедельник
            (1, "09:00", "21:00"),  # Вторник
            (2, "09:00", "21:00"),  # Среда
            (3, "09:00", "21:00"),  # Четверг
            (4, "09:00", "21:00"),  # Пятница
            (5, "09:00", "21:00"),  # Суббота
            (6, "09:00", "21:00"),  # Воскресенье
        ]

        for day_num, start_time, end_time in days:
            workday, created = WorkDay.objects.get_or_create(day=day_num, start_time=start_time, end_time=end_time)
            msg = f"Рабочее время - {workday.get_human_short_day()} {start_time} - {end_time}"
            if created:
                self.stdout.write(msg=msg, style_func=self.style.SUCCESS)
            else:
                self.stdout.write(msg=msg, style_func=self.style.WARNING, ending=" уже существует\n")
