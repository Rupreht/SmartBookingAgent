# pylint: disable=C0116
"Tests"

import datetime

from django.test import TestCase
from django.utils import timezone

from .models import ServiceLocation, WorkDay


class WorkDayTestCase(TestCase):
    "WorkDay Test"

    def setUp(self):
        self.workday = WorkDay.objects.create(day=0, start_time=datetime.time(8, 0), end_time=datetime.time(19, 0))

    def test_str_method(self):
        self.assertEqual(str(self.workday), "08:00-19:00 Понедельник")

    def test_is_time_available(self):
        time = datetime.time(12, 0)
        self.assertTrue(self.workday.is_time_available(time))

        time_before = datetime.time(7, 0)
        self.assertFalse(self.workday.is_time_available(time_before))

        time_after = datetime.time(19, 30)
        self.assertFalse(self.workday.is_time_available(time_after))

    def test_unique_together(self):
        with self.assertRaises(Exception):
            WorkDay.objects.create(day=0, start_time=datetime.time(8, 0), end_time=datetime.time(19, 0))


class ServiceLocationTestCase(TestCase):
    "ServiceLocation Test"

    def setUp(self):
        self.workday = WorkDay.objects.create(day=0, start_time=datetime.time(8, 0), end_time=datetime.time(19, 0))
        self.service_location = ServiceLocation.objects.create(
            name="Test Location",
            city="Москва",
            rest_of_address="ул. Примерная, д. 1",
            latitude=55.7558,
            longitude=37.6173,
            capacity=10,
        )
        self.service_location.available_days.add(self.workday)

    def test_str_method(self):
        self.assertEqual(str(self.service_location), "Test Location - Москва")

    def test_get_address(self):
        expected_address = "Москва, ул. Примерная, д. 1"
        self.assertEqual(self.service_location.get_address(), expected_address)

    def test_get_geo(self):
        expected_address = "55.7558, 37.6173"
        self.assertEqual(self.service_location.get_geo(), expected_address)

    def test_get_working_hours(self):
        expected_hours = "Понедельник 08:00-19:00"
        self.assertEqual(self.service_location.get_working_hours(), expected_hours)

    def test_is_available(self):
        date = timezone.datetime(2025, 8, 7)  # Четверг
        time = timezone.datetime(2025, 8, 7, 12, 0).time()
        self.assertFalse(self.service_location.is_available(date, time))

        self.service_location.available_days.add(
            WorkDay.objects.create(day=3, start_time=datetime.time(8, 0), end_time=datetime.time(11, 0))
        )
        self.assertFalse(self.service_location.is_available(date, time))
        self.assertTrue(self.service_location.is_available(date, timezone.datetime(2025, 8, 7, 10, 0).time()))

        expected_hours = "Понедельник 08:00-19:00, Четверг 08:00-11:00"
        self.assertEqual(self.service_location.get_working_hours(), expected_hours)
