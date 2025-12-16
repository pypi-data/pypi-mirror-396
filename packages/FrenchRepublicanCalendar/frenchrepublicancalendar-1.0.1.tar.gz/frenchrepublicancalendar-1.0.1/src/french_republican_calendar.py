# This file is part of French Republican Calendar Python Package.
# French Republican Calendar Python Package is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
# French Republican Calendar Python Package is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with French Republican Calendar Python Package.
# If not, see <https://www.gnu.org/licenses/>.
from datetime import date, timedelta

__author__ = "Nicolas Flandrois"
__credits__ = "Nicolas Flandrois"
__license__ = "GNU GPLv3, 2025, Nicolas Flandrois"
__created_on__ = "2025-12-10"
__maintainer__ = ["Nicolas Flandrois"]
__email__ = ["contacts@flandrois.com"]
__compatible_python_version__ = "≥ 3.12"
__status__ = "Production"
__version__ = "1.0.1"
__last_modified_on__ = "2025-12-11"


class RepublicanCalendar:
    def __init__(self, reference_epoch: date = None):
        """
        Initialize Republican Calendar converter.

        Args:
            reference_epoch: Date for Republican Year I (default: 1792-09-22)
        """
        self.reference_epoch = reference_epoch or date(1792, 9, 22)
        self.months = [
            "Vendémiaire",
            "Brumaire",
            "Frimaire",
            "Nivôse",
            "Pluviôse",
            "Ventôse",
            "Germinal",
            "Floréal",
            "Prairial",
            "Messidor",
            "Thermidor",
            "Fructidor",
        ]
        self.sansculottides = [
            "Jour de la vertu",
            "Jour du génie",
            "Jour du travail",
            "Jour de l'opinion",
            "Jour des récompenses",
            "Jour de la révolution",
        ]

    def _is_republican_leap_year(self, year: int) -> bool:
        """Check if Republican year is leap (6 sansculottides).
        According to French Republican Calendar definition of leap year

        Republican leap years: 3, 7, 11, 15, ...
        (when (year+1) % 4 == 0)"""
        return (year + 1) % 4 == 0

    def gregorian_to_republican(self, greg_date: date) -> tuple:
        """
        Convert Gregorian date to Republican date.

        Returns:
            (year, month, day, sansculottide) where sansculottide is None for regular days
        """
        days_diff = (greg_date - self.reference_epoch).days

        # Find the Republican year by subtracting days of complete years
        year = 1
        remaining_days = days_diff

        while True:
            is_leap = self._is_republican_leap_year(year)
            days_in_this_year = 365 + (1 if is_leap else 0)

            if remaining_days < days_in_this_year:
                break

            remaining_days -= days_in_this_year
            year += 1

        # 'remaining_days' now contains the day number
        # within the current Republican year (0-indexed)
        days_in_year = remaining_days
        is_leap = self._is_republican_leap_year(year)
        sansculottides_count = 6 if is_leap else 5

        if days_in_year >= 360:
            sansculottide_index = days_in_year - 360
            if sansculottide_index < sansculottides_count:
                return (year, None, None, self.sansculottides[sansculottide_index])
            else:
                raise ValueError(f"Invalid sansculottide index: {sansculottide_index}")

        month = days_in_year // 30
        day = (days_in_year % 30) + 1
        return (year, self.months[month], day, None)

    def republican_to_gregorian(self, year: int, month: str = None, day: int = None, sansculottide: str = None) -> date:
        """
        Convert Republican date to Gregorian date.
        """
        # Calculate total days from all previous years
        total_days = 0
        for y in range(1, year):
            total_days += 365 + (1 if self._is_republican_leap_year(y) else 0)

        if sansculottide is not None:
            sansculottide_index = self.sansculottides.index(sansculottide)
            total_days += 360 + sansculottide_index
        else:
            month_index = self.months.index(month)
            total_days += (month_index * 30) + (day - 1)

        return self.reference_epoch + timedelta(days=total_days)

    def now(self) -> tuple:
        """Convert current datetime to Republican date."""
        return self.gregorian_to_republican(date.today())

    def format_republican_date(self, rep_date: tuple) -> str:
        """Format Republican date tuple to readable string."""
        year, month, day, sansculottide = rep_date
        if sansculottide:
            return f"{sansculottide} Year {year}"
        return f"{day} {month} Year {year}"
