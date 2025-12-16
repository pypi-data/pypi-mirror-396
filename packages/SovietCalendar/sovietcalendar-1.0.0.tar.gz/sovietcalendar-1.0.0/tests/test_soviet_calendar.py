# This file is part of Soviet Calendar Python Package.
# Soviet Calendar Python Package is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
# Soviet Calendar Python Package is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with Soviet Calendar Python Package.
# If not, see <https://www.gnu.org/licenses/>.
import unittest
from datetime import date
from soviet_calendar import SovietCalendar

__author__ = "Nicolas Flandrois"
__credits__ = "Nicolas Flandrois"
__license__ = "GNU GPLv3, 2025, Nicolas Flandrois"
__created_on__ = "2025-12-10"
__maintainer__ = ["Nicolas Flandrois"]
__email__ = ["contacts@flandrois.com"]
__compatible_python_version__ = "≥ 3.12"
__status__ = "Production"
__version__ = "1.0.0"
__last_modified_on__ = "2025-12-11"


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
