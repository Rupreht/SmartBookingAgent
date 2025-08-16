from django.core.management.base import BaseCommand
from bot_admin.models import WorkDay


class Command(BaseCommand):
    help = 'Заполняет модель WorkDay данными о рабочих днях'

    def handle(self, *args, **kwargs):
        self.populate_work_days()

    def populate_work_days(self):
        days = [
            (0, "09:00:00", "18:00:00"),  # Понедельник
            (1, "09:00:00", "18:00:00"),  # Вторник
            (2, "09:00:00", "18:00:00"),  # Среда
            (3, "09:00:00", "18:00:00"),  # Четверг
            (4, "09:00:00", "18:00:00"),  # Пятница
            (5, "09:00:00", "18:00:00"),  # Суббота
            (6, "09:00:00", "18:00:00"),  # Воскресенье

            (0, "10:00:00", "19:00:00"),  # Понедельник
            (1, "10:00:00", "19:00:00"),  # Вторник
            (2, "10:00:00", "19:00:00"),  # Среда
            (3, "10:00:00", "19:00:00"),  # Четверг
            (4, "10:00:00", "19:00:00"),  # Пятница
            (5, "10:00:00", "19:00:00"),  # Суббота
            (6, "10:00:00", "19:00:00"),  # Воскресенье

            (0, "09:00:00", "21:00:00"),  # Понедельник
            (1, "09:00:00", "21:00:00"),  # Вторник
            (2, "09:00:00", "21:00:00"),  # Среда
            (3, "09:00:00", "21:00:00"),  # Четверг
            (4, "09:00:00", "21:00:00"),  # Пятница
            (5, "09:00:00", "21:00:00"),  # Суббота
            (6, "09:00:00", "21:00:00"),  # Воскресенье
        ]

        for day_num, start_time, end_time in days:
            work_day, created = WorkDay.objects.get_or_create(
                day=day_num, start_time=start_time, end_time=end_time)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан день {day_num} {start_time}-{end_time}'))
            else:
                self.stdout.write(self.style.WARNING(f'День {day_num} {start_time}-{end_time} уже существует'))
