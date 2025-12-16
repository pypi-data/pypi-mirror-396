# This file is part of Soviet Calendar Python Package.
# Soviet Calendar Python Package is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
# Soviet Calendar Python Package is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with Soviet Calendar Python Package.
# If not, see <https://www.gnu.org/licenses/>.
from datetime import datetime, date

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


class SovietCalendar:
    """
    Represents a Gregorian date interpreted under the Soviet continuous work-week system
    (1929–1940). Only the weekly cycle was altered; year/month/day (yyyy/mm/dd) remain Gregorian.
    """

    def __init__(self, dt: datetime | date):
        if isinstance(dt, datetime):
            self.dt = dt.date()
        elif isinstance(dt, date):
            self.dt = dt
        else:
            raise TypeError("Input must be datetime or date")

        if not (date(1929, 1, 1) <= self.dt <= date(1940, 6, 26)):
            raise ValueError("Soviet calendar system was only used from 1929-01-01 to 1940-06-26")

    @property
    def gregorian_date(self) -> date:
        return self.dt

    @property
    def five_day_week_day(self) -> int:
        """Return 1–5; based on continuous 5-day cycle starting 1929-01-01 as day 1."""
        days_since_start = (self.dt - date(1929, 1, 1)).days
        return (days_since_start % 5) + 1

    @property
    def six_day_week_day(self) -> int:
        """Return 1–6; based on 6-day cycle starting 1929-12-01 (first official month)."""
        # The 6-day week officially began December 1929, but widely used from 1931.
        # We anchor to 1929-12-01 as day 1 for consistency.
        anchor = date(1929, 12, 1)
        if self.dt < anchor:
            # Before Dec 1929, extrapolate backward from anchor
            days = (self.dt - anchor).days
            return ((days % 6) + 6) % 6 + 1
        else:
            days = (self.dt - anchor).days
            return (days % 6) + 1

    @classmethod
    def now(cls):
        """Return SovietCalendar for current date (only valid if within 1929–1940)."""
        today = date.today()
        try:
            return cls(today)
        except ValueError as e:
            return f"Soviet calendar not in use on {today}: {e}"

    def __repr__(self):
        return f"SovietCalendar({self.dt.isoformat()}, 5-day: {self.five_day_week_day}, 6-day: {self.six_day_week_day})"
