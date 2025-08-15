"""django.test"""

from django.test import TestCase


class SimpleTest(TestCase):
    """Тесты"""

    def test_basic_addition(self):
        "Тесты должны иметь имена, начинающиеся с test_."
        self.assertEqual(1 + 1, 2)
