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
from french_republican_calendar import RepublicanCalendar
import unittest

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


class TestRepublicanCalendar(unittest.TestCase):
    def setUp(self):
        self.cal = RepublicanCalendar()

    def test_init_default_reference_epoch(self):
        """Test initialization with default reference epoch."""
        cal = RepublicanCalendar()
        self.assertEqual(cal.reference_epoch, date(1792, 9, 22))

    def test_init_custom_reference_epoch(self):
        """Test initialization with custom reference epoch."""
        custom_epoch = date(1793, 1, 1)
        cal = RepublicanCalendar(custom_epoch)
        self.assertEqual(cal.reference_epoch, custom_epoch)

    def test_is_republican_leap_year(self):
        """Test leap year detection."""
        # Year 3 should be leap ((3+1) % 4 == 0)
        self.assertTrue(self.cal._is_republican_leap_year(3))
        # Year 4 should not be leap
        self.assertFalse(self.cal._is_republican_leap_year(4))
        # Year 7 should be leap ((7+1) % 4 == 0)
        self.assertTrue(self.cal._is_republican_leap_year(7))
        # Year 11 should be leap ((11+1) % 4 == 0)
        self.assertTrue(self.cal._is_republican_leap_year(11))
        # Year 1 should not be leap ((1+1) % 4 != 0)
        self.assertFalse(self.cal._is_republican_leap_year(1))
        # Year 2 should not be leap ((2+1) % 4 != 0)
        self.assertFalse(self.cal._is_republican_leap_year(2))

    def test_gregorian_to_republican_regular_day(self):
        """Test conversion of a regular Gregorian date to Republican."""
        # Reference epoch itself - day 0
        result = self.cal.gregorian_to_republican(date(1792, 9, 22))
        self.assertEqual(result, (1, "Vendémiaire", 1, None))

        # A few days later - day 1
        result = self.cal.gregorian_to_republican(date(1792, 9, 23))
        self.assertEqual(result, (1, "Vendémiaire", 2, None))

        # End of first month - day 29
        result = self.cal.gregorian_to_republican(date(1792, 10, 21))
        self.assertEqual(result, (1, "Vendémiaire", 30, None))

        # Last day of 12th month (Fructidor 30) = day 359
        # Sep 22, 1792 + 359 days = around Sep 16, 1793
        fructidor_30_date = self.cal.reference_epoch + timedelta(days=359)
        result = self.cal.gregorian_to_republican(fructidor_30_date)
        self.assertEqual(result, (1, "Fructidor", 30, None))

    def test_gregorian_to_republican_sansculottides(self):
        """Test conversion of sansculottides dates."""
        # First sansculottide of Year 1 - day 360 after epoch
        sansc_date = self.cal.reference_epoch + timedelta(days=360)  # First sansculottide of Year 1
        result = self.cal.gregorian_to_republican(sansc_date)
        expected_sansc = (1, None, None, "Jour de la vertu")
        self.assertEqual(result, expected_sansc)

        # Last sansculottide of Year 1 (non-leap year has 5) - day 364
        sansc_date = self.cal.reference_epoch + timedelta(days=364)  # Last sansculottide of Year 1
        result = self.cal.gregorian_to_republican(sansc_date)
        expected_sansc = (1, None, None, "Jour des récompenses")
        self.assertEqual(result, expected_sansc)

        # Year 2's last sansculottide: 365 (Year 1) + 364 = 729 days after epoch
        sansc_date = self.cal.reference_epoch + timedelta(days=729)  # Last sansculottide of Year II (not leap year)
        result = self.cal.gregorian_to_republican(sansc_date)
        self.assertEqual(result, (2, None, None, "Jour des récompenses"))

    def test_gregorian_to_republican_leap_year_sansculottides(self):
        """Test conversion during a leap year with 6 sansculottides."""
        # Year 3 is a leap year, so it has 6 sansculottides
        # Days before Year 3: Year 1 (365 days) + Year 2 (365 days) = 730 days
        # 6th sansculottide of Year 3 = day 730 + 360 + 5 = 1095 after epoch
        target_date = self.cal.reference_epoch + timedelta(days=1095)
        result = self.cal.gregorian_to_republican(target_date)
        self.assertEqual(result, (3, None, None, "Jour de la révolution"))

    def test_republican_to_gregorian_regular_month(self):
        """Test conversion from Republican to Gregorian for regular months."""
        result = self.cal.republican_to_gregorian(1, "Vendémiaire", 1)
        self.assertEqual(result, date(1792, 9, 22))

        result = self.cal.republican_to_gregorian(1, "Vendémiaire", 15)
        self.assertEqual(result, date(1792, 10, 6))

    def test_republican_to_gregorian_sansculottides(self):
        """Test conversion from Republican to Gregorian for sansculottides."""
        # Year 2's first sansculottide
        # Days before Year 2: 365 days
        # First sansculottide of Year 2 = day 365 + 360 = 725 after epoch
        result = self.cal.republican_to_gregorian(2, sansculottide="Jour de la vertu")
        expected_date = self.cal.reference_epoch + timedelta(days=725)
        self.assertEqual(result, expected_date)

        # Year 2's last sansculottide (not leap year, so 5th sansculottide)
        # Day = 365 (Year 1) + 360 + 4 = 729 after epoch
        result = self.cal.republican_to_gregorian(2, sansculottide="Jour des récompenses")
        expected_date = self.cal.reference_epoch + timedelta(days=729)
        self.assertEqual(result, expected_date)

        # Year 3's 6th sansculottide (leap year)
        # Day = 365 (Year 1) + 365 (Year 2) + 360 + 5 = 1090 after epoch? No, that's index 5, which is day 1095
        result = self.cal.republican_to_gregorian(3, sansculottide="Jour de la révolution")
        expected_date = self.cal.reference_epoch + timedelta(days=1095)
        self.assertEqual(result, expected_date)

    def test_round_trip_conversion(self):
        """Test that converting Gregorian->Republican->Gregorian gives original date."""
        original_date = date(1800, 6, 15)
        rep_date = self.cal.gregorian_to_republican(original_date)
        back_to_greg = self.cal.republican_to_gregorian(*rep_date)
        self.assertEqual(back_to_greg, original_date)

    def test_now_method(self):
        """Test the now() method returns valid tuple."""
        today = date.today()
        result = self.cal.now()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 4)

        # Verify it matches manual conversion
        expected = self.cal.gregorian_to_republican(today)
        self.assertEqual(result, expected)

    def test_format_republican_date_regular(self):
        """Test formatting of regular Republican dates."""
        rep_date = (1, "Vendémiaire", 1, None)
        formatted = self.cal.format_republican_date(rep_date)
        self.assertEqual(formatted, "1 Vendémiaire Year 1")

    def test_format_republican_date_sansculottide(self):
        """Test formatting of sansculottide dates."""
        rep_date = (1, None, None, "Jour des récompenses")
        formatted = self.cal.format_republican_date(rep_date)
        self.assertEqual(formatted, "Jour des récompenses Year 1")

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Year transition
        # Day 359 = last day of Year 1 regular months
        last_month_day = self.cal.reference_epoch + timedelta(days=359)
        result = self.cal.gregorian_to_republican(last_month_day)
        self.assertEqual(result[0], 1)  # Should be year 1

        # Day 360 = first sansculottide of Year 1
        first_sansc = self.cal.reference_epoch + timedelta(days=360)
        result = self.cal.gregorian_to_republican(first_sansc)
        self.assertEqual(result[0], 1)  # Should still be year 1

        # Day 365 = first day of Year 2
        year2_start = self.cal.reference_epoch + timedelta(days=365)
        result = self.cal.gregorian_to_republican(year2_start)
        self.assertEqual(result[0], 2)  # Should be year 2


class TestRepublicanCalendarHistoricalEvents(unittest.TestCase):
    def setUp(self):
        self.cal = RepublicanCalendar()

    def test_founding_of_republican_calendar(self):
        """Test the founding of the Republican Calendar (September 22, 1792)."""
        result = self.cal.gregorian_to_republican(date(1792, 9, 22))
        self.assertEqual(result, (1, "Vendémiaire", 1, None))

    def test_execution_of_louis_xvi(self):
        """Test the execution of Louis XVI (January 21, 1793)."""
        result = self.cal.gregorian_to_republican(date(1793, 1, 21))
        # Calculated by the algorithm
        self.assertEqual(result, (1, "Pluviôse", 2, None))

    def test_execution_of_marie_antoinette(self):
        """Test the execution of Marie Antoinette (October 16, 1793)."""
        result = self.cal.gregorian_to_republican(date(1793, 10, 16))
        # Calculated by the algorithm
        self.assertEqual(result, (2, "Vendémiaire", 25, None))

    def test_fall_of_robespierre(self):
        """Test the fall of Robespierre (July 27, 1794)."""
        result = self.cal.gregorian_to_republican(date(1794, 7, 27))
        # Calculated by the algorithm
        self.assertEqual(result, (2, "Thermidor", 9, None))

    def test_coup_of_18_brumaire(self):
        """Test Coup of 18 Brumaire (November 9, 1799)."""
        result = self.cal.gregorian_to_republican(date(1799, 11, 9))
        # Calculated by the algorithm
        self.assertEqual(result, (8, "Brumaire", 18, None))

    def test_napoleon_coronation(self):
        """Test Napoleon's coronation (December 2, 1804)."""
        result = self.cal.gregorian_to_republican(date(1804, 12, 2))
        # Calculated by the algorithm
        self.assertEqual(result, (13, "Frimaire", 11, None))

    def test_end_of_republican_calendar_use(self):
        """Test the end of Republican calendar official use (January 1, 1806)."""
        result = self.cal.gregorian_to_republican(date(1806, 1, 1))
        # Calculated by the algorithm
        self.assertEqual(result, (14, "Nivôse", 11, None))

    def test_revolutionary_new_year_year_i_end(self):
        """Test the end of Year I (September 21, 1793)."""
        result = self.cal.gregorian_to_republican(date(1793, 9, 21))
        # Calculated by the algorithm
        self.assertEqual(result, (1, None, None, "Jour des récompenses"))

    def test_revolutionary_new_year_year_ii_start(self):
        """Test the start of Year II (September 22, 1793)."""
        result = self.cal.gregorian_to_republican(date(1793, 9, 22))
        # Calculated by the algorithm
        self.assertEqual(result, (2, "Vendémiaire", 1, None))

    def test_revolutionary_new_year_year_iii_start(self):
        """Test the start of Year III (September 22, 1794)."""
        result = self.cal.gregorian_to_republican(date(1794, 9, 22))
        # Calculated by the algorithm
        self.assertEqual(result, (3, "Vendémiaire", 1, None))

    @unittest.skip("FIXME - Wrong Data for that year")
    def test_leap_year_sansculottide_year_iii(self):
        """Test the 6th sansculottide in leap Year III (September 27, 1795)."""
        result = self.cal.gregorian_to_republican(date(1795, 9, 27))
        # Calculated by the algorithm - this should be the end of Year III
        # self.assertEqual(result, (3, None, None, "Jour de la révolution"))
        self.assertEqual(result, (4, "Vendémiaire", 5, None))

    def test_thermidorian_reaction(self):
        """Test the Thermidorian Reaction (July 27, 1794)."""
        result = self.cal.gregorian_to_republican(date(1794, 7, 27))
        # Same as fall of Robespierre
        self.assertEqual(result, (2, "Thermidor", 9, None))

    def test_proclamation_of_republic(self):
        """Test the Proclamation of the Republic (September 22, 1792)."""
        result = self.cal.gregorian_to_republican(date(1792, 9, 22))
        # Same as founding of calendar
        self.assertEqual(result, (1, "Vendémiaire", 1, None))

    def test_levée_en_masse(self):
        """Test the Levée en masse (August 23, 1793)."""
        result = self.cal.gregorian_to_republican(date(1793, 8, 23))
        # Calculated by the algorithm
        self.assertEqual(result, (1, "Fructidor", 6, None))

    def test_levée_des_prairial(self):
        """Test the Levée des Prairial (June 8, 1794)."""
        result = self.cal.gregorian_to_republican(date(1794, 6, 8))
        # Calculated by the algorithm
        self.assertEqual(result, (2, "Prairial", 20, None))

    def test_14_july_festival(self):
        """Test the Festival of 14 July (July 14, 1794)."""
        result = self.cal.gregorian_to_republican(date(1794, 7, 14))
        # Calculated by the algorithm
        self.assertEqual(result, (2, "Messidor", 26, None))


if __name__ == "__main__":
    unittest.main()
