# test_soviet_calendar.py
import unittest
from datetime import date
from soviet_calendar import SovietCalendar


class TestSovietCalendar(unittest.TestCase):

    def test_valid_date_in_range(self):
        sc = SovietCalendar(date(1930, 5, 1))
        self.assertEqual(sc.gregorian_date, date(1930, 5, 1))
        self.assertEqual(sc.five_day_week_day, 1)
        self.assertEqual(sc.six_day_week_day, 2)

    def test_boundary_start_1929_01_01(self):
        sc = SovietCalendar(date(1929, 1, 1))
        self.assertEqual(sc.five_day_week_day, 1)
        self.assertEqual(sc.six_day_week_day, 3)  # (-334 % 6) + 1 = 2 + 1 = 3

    def test_boundary_end_1940_06_26(self):
        sc = SovietCalendar(date(1940, 6, 26))
        self.assertIsInstance(sc.five_day_week_day, int)
        self.assertIsInstance(sc.six_day_week_day, int)

    def test_date_before_1929_raises(self):
        with self.assertRaises(ValueError):
            SovietCalendar(date(1928, 12, 31))

    def test_date_after_1940_raises(self):
        with self.assertRaises(ValueError):
            SovietCalendar(date(1940, 6, 27))

    def test_invalid_input_type(self):
        with self.assertRaises(TypeError):
            SovietCalendar("1930-05-01")

    def test_repr_format(self):
        sc = SovietCalendar(date(1930, 5, 1))
        self.assertIn("1930-05-01", repr(sc))
        self.assertIn("5-day: 1", repr(sc))
        self.assertIn("6-day: 2", repr(sc))

    def test_gregorian_date_property(self):
        d = date(1935, 11, 7)
        sc = SovietCalendar(d)
        self.assertIs(sc.gregorian_date, d)

    def test_five_day_cycle_consistency(self):
        # 5-day cycle should repeat every 5 days
        base = SovietCalendar(date(1930, 1, 1))
        later = SovietCalendar(date(1930, 1, 6))  # +5 days
        self.assertEqual(base.five_day_week_day, later.five_day_week_day)

    def test_six_day_cycle_consistency(self):
        # 6-day cycle repeats every 6 days from anchor (1929-12-01)
        base = SovietCalendar(date(1930, 12, 1))
        later = SovietCalendar(date(1930, 12, 7))  # +6 days
        self.assertEqual(base.six_day_week_day, later.six_day_week_day)


if __name__ == "__main__":
    unittest.main()
