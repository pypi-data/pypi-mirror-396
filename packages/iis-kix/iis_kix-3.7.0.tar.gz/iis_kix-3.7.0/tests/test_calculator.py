import unittest

from iis_frida.model.common.calculator import add


class TestCalculator(unittest.TestCase):

    def test_add(self):
        self.assertEqual(add(1, 2), 3)  # Test case 1
        self.assertEqual(add(-1, 1), 0)  # Test case 2
        self.assertEqual(add(0, 0), 0)   # Test case 3