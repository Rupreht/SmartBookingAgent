"Загружает в базу тестовых пользователей Telegram"

from django.core.management.base import BaseCommand
from bot_admin.models import TelegramUser
import random  # Добавлен импорт модуля random


class Command(BaseCommand):
    "Класс для создания в manage под-команды"

    help = "Заполняет модель TelegramUser тестовыми данными"
    output_transaction = True
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument("number", type=int, help="Количество тестовых пользователей для создания")

    def handle(self, *args, **kwargs) -> None:
        count = kwargs["number"] if "number" in kwargs else 10
        self.setup_test_telegram_users(count)

    def setup_test_telegram_users(self, count=10):
        "Заполняет модель TelegramUser тестовыми данными"
        test_users = [
            {
                "id": random.randint(1000000000, 2000000000),  # Изменено формирование id
                "is_bot": False,
                "first_name": f"User{i}",
                "username": f"testuser{i}" if i % 2 == 0 else None,
                "language_code": "en" if i % 3 == 0 else "ru",
                "is_premium": i % 4 == 0,
                "added_to_attachment_menu": i % 5 == 0,
                "can_connect_to_business": i % 6 == 0,
            }
            for i in range(0, count)
        ]
        created_count = 0  # Переименована переменная для избежания конфликта с параметром count
        for user_data in test_users:
            _, created = TelegramUser.objects.get_or_create(**user_data)
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} test Telegram users"))
        return True
