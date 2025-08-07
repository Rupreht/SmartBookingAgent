from django.test import TestCase
from django.utils import timezone
from .models import WeekDay, ServiceLocation


class WeekDayTestCase(TestCase):
    def setUp(self):
        self.weekday = WeekDay.objects.create(day=0, start_time="09:00", end_time="18:00")

    def test_str_method(self):
        self.assertEqual(str(self.weekday), "09:00-18:00 Понедельник")

    def test_is_time_available(self):
        time = timezone.datetime(2025, 8, 7, 12, 0).time()
        self.assertTrue(self.weekday.is_time_available(time))

        time_before = timezone.datetime(2025, 8, 7, 8, 0).time()
        self.assertFalse(self.weekday.is_time_available(time_before))

        time_after = timezone.datetime(2025, 8, 7, 19, 0).time()
        self.assertFalse(self.weekday.is_time_available(time_after))

    def test_unique_together(self):
        with self.assertRaises(Exception):
            WeekDay.objects.create(day=0, start_time="09:00", end_time="18:00")


class ServiceLocationTestCase(TestCase):
    def setUp(self):
        self.weekday = WeekDay.objects.create(day=0, start_time="09:00", end_time="18:00")
        self.service_location = ServiceLocation.objects.create(
            name="Test Location", city="Москва", rest_of_address="ул. Примерная, д. 1", latitude=55.7558, longitude=37.6173, capacity=10
        )
        self.service_location.available_days.add(self.weekday)

    def test_get_address(self):
        expected_address = "Москва, ул. Примерная, д. 1 (55.7558, 37.6173)"
        self.assertEqual(self.service_location.get_address(), expected_address)

    def test_get_working_hours(self):
        expected_hours = "Понедельник 09:00-18:00"
        self.assertEqual(self.service_location.get_working_hours(), expected_hours)

    def test_is_available(self):
        date = timezone.datetime(2025, 8, 7)  # Четверг
        time = timezone.datetime(2025, 8, 7, 12, 0).time()
        self.assertFalse(self.service_location.is_available(date, time))

        self.service_location.available_days.add(WeekDay.objects.create(day=3))
        self.assertTrue(self.service_location.is_available(date, time))
