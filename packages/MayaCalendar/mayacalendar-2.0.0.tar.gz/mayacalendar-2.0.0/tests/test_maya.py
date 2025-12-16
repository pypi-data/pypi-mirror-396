# This file is part of Maya Calendar Python Package.
# Maya Calendar Python Package is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
# Maya Calendar Python Package is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with Maya Calendar Python Package.
# If not, see <https://www.gnu.org/licenses/>.
import unittest
from datetime import datetime

from mayacalendar import MayaDate

__author__ = "Nicolas Flandrois"
__credits__ = "Nicolas Flandrois"
__license__ = "GNU GPLv3, 2025, Nicolas Flandrois"
__created_on__ = "2025-12-10"
__maintainer__ = ["Nicolas Flandrois"]
__email__ = ["contacts@flandrois.com"]
__compatible_python_version__ = "≥ 3.12"
__status__ = "Production"
__version__ = "1.2.2"
__last_modified_on__ = "2025-12-13"


class TestMayaDate(unittest.TestCase):

    def setUp(self):
        self.gmt_converter = MayaDate(correlation='GMT')
        self.spinden_converter = MayaDate(correlation='Spinden')

    def test_correlation_difference(self):
        """Test that GMT and Spinden correlations produce different results"""
        test_date = datetime(2024, 1, 1)

        gmt_lc = self.gmt_converter.gregorian_to_long_count(test_date)
        spinden_lc = self.spinden_converter.gregorian_to_long_count(test_date)

        # Should be 2 days different
        gmt_parts = list(map(int, gmt_lc.split('.')))
        spinden_parts = list(map(int, spinden_lc.split('.')))

        # Calculate total days for comparison
        gmt_total = sum([a * b for a, b in zip(gmt_parts, [144000, 7200, 360, 20, 1])])
        spinden_total = sum([a * b for a, b in zip(spinden_parts, [144000, 7200, 360, 20, 1])])

        self.assertEqual(gmt_total - spinden_total, 2,
                         f"GMT ({gmt_lc}) and Spinden ({spinden_lc}) should be 2 days apart")

    def test_long_count_conversion_round_trip(self):
        """Test converting Gregorian->Long Count->Gregorian"""
        original_date = datetime(2024, 6, 15)

        long_count = self.gmt_converter.gregorian_to_long_count(original_date)
        returned_date = self.gmt_converter.long_count_to_gregorian(long_count)

        self.assertEqual(returned_date.date(), original_date.date())

    def test_gregorian_to_long_count(self):
        """Test known conversion"""
        # Known date: Dec 21, 2012 was 13.0.0.0.0
        date_2012 = datetime(2012, 12, 21)
        expected = "13.0.0.0.0"
        result = self.gmt_converter.gregorian_to_long_count(date_2012)
        self.assertEqual(result, expected)

    def test_gregorian_to_tzolkin(self):
        """Test Tzolkin conversion"""
        test_date = datetime(2024, 1, 1)
        tzolkin = self.gmt_converter.gregorian_to_tzolkin(test_date)

        # Should be in format "number name"
        parts = tzolkin.split(' ')
        self.assertEqual(len(parts), 2)

        number_part = int(parts[0])
        name_part = parts[1]

        self.assertTrue(1 <= number_part <= 13)
        self.assertIn(name_part, self.gmt_converter.tzolkin_names)

    def test_gregorian_to_haab(self):
        """Test Haab' conversion"""
        test_date = datetime(2024, 1, 1)
        haab = self.gmt_converter.gregorian_to_haab(test_date)

        # Should be in format "number month" or "number Uayeb"
        parts = haab.split(' ')
        self.assertEqual(len(parts), 2)

        day_num = int(parts[0])
        month_name = parts[1]

        self.assertTrue(0 <= day_num <= 19 or 0 <= day_num <= 4 and month_name == 'Uayeb')
        if month_name != 'Uayeb':
            self.assertIn(month_name, self.gmt_converter.haab_months)

    def test_long_count_to_gregorian(self):
        """Test Long Count to Gregorian conversion"""
        long_count = "13.0.0.0.0"  # Dec 21, 2012
        expected_date = datetime(2012, 12, 21)

        result = self.gmt_converter.long_count_to_gregorian(long_count)
        self.assertEqual(result.date(), expected_date.date())

    def test_tzolkin_now_classmethod(self):
        """Test tzolkin_now classmethod with different correlations"""
        gmt_result = MayaDate.tzolkin_now('GMT')
        spinden_result = MayaDate.tzolkin_now('Spinden')

        # Both should be valid Tzolkin formats
        gmt_parts = gmt_result.split(' ')
        spinden_parts = spinden_result.split(' ')

        self.assertEqual(len(gmt_parts), 2)
        self.assertEqual(len(spinden_parts), 2)

        gmt_num = int(gmt_parts[0])
        spinden_num = int(spinden_parts[0])

        self.assertTrue(1 <= gmt_num <= 13)
        self.assertTrue(1 <= spinden_num <= 13)

    def test_haab_now_classmethod(self):
        """Test haab_now classmethod"""
        result = MayaDate.haab_now()
        parts = result.split(' ')

        self.assertEqual(len(parts), 2)
        day_num = int(parts[0])
        month_name = parts[1]

        self.assertTrue(0 <= day_num <= 19 or 0 <= day_num <= 4 and month_name == 'Uayeb')
        if month_name != 'Uayeb':
            self.assertIn(month_name, self.gmt_converter.haab_months)

    def test_long_count_now_classmethod(self):
        """Test long_count_now classmethod with different correlations"""
        gmt_result = MayaDate.long_count_now('GMT')
        spinden_result = MayaDate.long_count_now('Spinden')

        # Both should be valid Long Count formats
        gmt_parts = list(map(int, gmt_result.split('.')))
        spinden_parts = list(map(int, spinden_result.split('.')))

        self.assertEqual(len(gmt_parts), 5)
        self.assertEqual(len(spinden_parts), 5)

        # Check ranges (should be reasonable values for current era)
        self.assertLessEqual(gmt_parts[0], 13)  # Baktun
        self.assertLessEqual(spinden_parts[0], 13)

    def test_invalid_correlation_defaults_to_gmt(self):
        """Test that invalid correlation defaults to GMT"""
        converter = MayaDate(correlation='INVALID')
        # Should use GMT reference (584283)
        self.assertEqual(converter.julian_ref, 584283)

    def test_known_dates(self):
        """Test some known historical correlations"""
        # December 21, 2012 = end of 13th baktun
        date_2012 = datetime(2012, 12, 21)
        expected_lc = "13.0.0.0.0"
        result = self.gmt_converter.gregorian_to_long_count(date_2012)
        self.assertEqual(result, expected_lc)

    def test_uayeb_days(self):
        """Test that Uayeb days are handled correctly"""
        # These should fall in the Uayeb period (end of Haab' year)
        uayeb_test_date = datetime(2024, 12, 31)  # Close to end of year
        haab = self.gmt_converter.gregorian_to_haab(uayeb_test_date)

        # Verify format
        parts = haab.split(' ')
        self.assertEqual(len(parts), 2)
        if parts[1] == 'Uayeb':
            day_num = int(parts[0])
            self.assertTrue(0 <= day_num <= 4)

    def test_spinden_correlation_specific_difference(self):
        """Specific test for 2-day difference between correlations"""
        test_date = datetime(2025, 1, 1)

        gmt_lc = self.gmt_converter.gregorian_to_long_count(test_date)
        spinden_lc = self.spinden_converter.gregorian_to_long_count(test_date)

        # Parse both and verify 2-day difference
        gmt_kin = int(gmt_lc.split('.')[-1])
        spinden_kin = int(spinden_lc.split('.')[-1])

        # Account for potential day wrapping
        expected_diff = (gmt_kin - spinden_kin) % 20
        self.assertEqual(expected_diff, 2, f"Kin difference should be 2, got {expected_diff}")


if __name__ == '__main__':
    unittest.main()
