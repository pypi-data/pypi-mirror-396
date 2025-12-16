# This file is part of Maya Calendar Python Package.
# Maya Calendar Python Package is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
# Maya Calendar Python Package is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with Maya Calendar Python Package.
# If not, see <https://www.gnu.org/licenses/>.
from datetime import datetime

__author__ = "Nicolas Flandrois"
__credits__ = "Nicolas Flandrois"
__license__ = "GNU GPLv3, 2025, Nicolas Flandrois"
__created_on__ = "2025-12-10"
__maintainer__ = ["Nicolas Flandrois"]
__email__ = ["contacts@flandrois.com"]
__compatible_python_version__ = "≥ 3.12"
__status__ = "Production"
__version__ = "1.2.2"
__last_modified_on__ = "2025-12-11"


class MayanDateConverter:
    """A Python library for converting between Gregorian and Mayan calendar systems.
    Supports all three traditional Mayan calendars: Long Count, Tzolkin, and Haab'.

    The Maya civilization developed multiple sophisticated calendar systems that worked together.
    This library provides accurate conversions between the Gregorian calendar and these three Mayan systems:

    The Three Mayan Calendars:

    1. Long Count
        - A linear count of days from a mythical creation date (August 11, 3114 BCE in the proleptic Gregorian calendar)
        - Format: Baktun.Katun.Tun.Uinal.Kin (e.g., 13.0.12.2.12)
        - Cycle: 5,125 years (13 baktuns)
        - Purpose: Historical and ceremonial dating
        - References:
            - Wikipedia: Mesoamerican Long Count calendar
                - https://en.wikipedia.org/wiki/Mesoamerican_Long_Count_calendar
    2. Tzolkin (Divine Calendar)
        - A 260-day sacred calendar combining 13 numbers with 20 day names
        - Cycle: 260 days (13 × 20)
        - Format: Number Name (e.g., 4 Ahau)
        - Purpose: Religious ceremonies, divination, naming
        - References:
            - Wikipedia: Tzolkin
                - https://en.wikipedia.org/wiki/Tzolk%CA%BCin
            - Time and the Highland Maya - Phd Barbara Tedlock (1992)
                - https://www.academia.edu/4380893/Barbara_Tedlock_Time_and_the_Highland_Maya_1992
    3. Haab' (Solar Calendar)
        - A 365-day solar calendar similar to our year
        - 18 months of 20 days each plus 5 "nameless" days (Uayeb)
        - Format: Day Month (e.g., 12 Kankin)
        - Purpose: Agricultural and seasonal tracking
        - References:
            - Wikipedia: Haab (Maya Calendar)
                - https://en.wikipedia.org/wiki/Haab%CA%BC_(Maya_calendar)
            - Time and the Highland Maya - Phd Barbara Tedlock (1992)
                - https://www.academia.edu/4380893/Barbara_Tedlock_Time_and_the_Highland_Maya_1992
    """
    def __init__(self, correlation: str = 'GMT'):
        """
        Initialize with correlation reference.
        Options: 'GMT' (default), 'Spinden'
        """
        correlations = {
            'GMT': 584283,  # Julian Day for Aug 11, 3114 BCE
            'Spinden': 584285  # Alternative correlation (2 days later)
        }
        self.julian_ref = correlations.get(correlation, 584283)

        self.tzolkin_names = [
            'Imix', 'Ik', 'Akbal', 'Kan', 'Chicchan', 'Cimi', 'Manik',
            'Lamat', 'Muluc', 'Oc', 'Chuen', 'Eb', 'Ben', 'Ix', 'Mem',
            'Cib', 'Caban', 'Etznab', 'Cauac', 'Ahau'
        ]

        self.haab_months = [
            'Pop', 'Uo', 'Zip', 'Zotz', 'Tzec', 'Xul', 'Yaxkin',
            'Mol', 'Chen', 'Yax', 'Zac', 'Ceh', 'Mac', 'Kankin',
            'Muan', 'Pax', 'Kayab', 'Cumku'
        ]

    def _datetime_to_julian(self, dt: datetime) -> int:
        """Convert datetime to Julian Day Number"""
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        return dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045

    def _julian_to_datetime(self, jdn: int) -> datetime:
        """Convert Julian Day Number back to datetime"""
        a = jdn + 32044
        b = (4 * a + 3) // 146097
        c = a - (146097 * b) // 4
        d = (4 * c + 3) // 1461
        e = c - (1461 * d) // 4
        m = (5 * e + 2) // 153

        day = e - (153 * m + 2) // 5 + 1
        month = m + 3 - 12 * (m // 10)
        year = 100 * b + d - 4800 + m // 10

        return datetime(year, month, day)

    def gregorian_to_long_count(self, dt: datetime) -> str:
        """Convert Gregorian to Long Count - now uses correct correlation"""
        jdn = self._datetime_to_julian(dt)
        days_since_creation = jdn - self.julian_ref  # This now varies by correlation

        baktun = days_since_creation // 144000
        remaining = days_since_creation % 144000
        katun = remaining // 7200
        remaining = remaining % 7200
        tun = remaining // 360
        remaining = remaining % 360
        uinal = remaining // 20
        kin = remaining % 20

        return f"{baktun}.{katun}.{tun}.{uinal}.{kin}"

    def long_count_to_gregorian(self, long_count: str) -> datetime:
        """Convert Long Count to Gregorian - now uses correct correlation"""
        baktun, katun, tun, uinal, kin = map(int, long_count.split('.'))
        total_days = baktun * 144000 + katun * 7200 + tun * 360 + uinal * 20 + kin
        jdn = self.julian_ref + total_days  # This now varies by correlation
        return self._julian_to_datetime(jdn)

    def gregorian_to_tzolkin(self, dt: datetime) -> str:
        """Convert Gregorian to Tzolkin - correlation affects this too"""
        jdn = self._datetime_to_julian(dt)
        days_since_creation = jdn - self.julian_ref  # Now varies by correlation
        tzolkin_num = ((days_since_creation + 8) % 13) + 1  # Starting from 9 Ik
        tzolkin_name_idx = (days_since_creation + 8) % 20
        return f"{tzolkin_num} {self.tzolkin_names[tzolkin_name_idx]}"

    def tzolkin_to_gregorian(self, tzolkin: str, reference_year: int = 2000) -> datetime:
        """Convert Tzolkin to Gregorian (approximate within reference year range)"""
        num_str, name = tzolkin.split(' ', 1)
        target_num = int(num_str)
        target_name_idx = self.tzolkin_names.index(name)

        ref_date = datetime(reference_year, 1, 1)
        ref_jdn = self._datetime_to_julian(ref_date)
        ref_days_since_creation = ref_jdn - self.julian_ref

        # Find matching Tzolkin date
        for day_offset in range(260):  # Search within 260-day cycle
            test_days_since_creation = ref_days_since_creation + day_offset
            calc_num = ((test_days_since_creation + 8) % 13) + 1
            calc_name_idx = (test_days_since_creation + 8) % 20

            if calc_num == target_num and calc_name_idx == target_name_idx:
                test_jdn = self.julian_ref + test_days_since_creation
                return self._julian_to_datetime(test_jdn)

        return ref_date  # Fallback

    def gregorian_to_haab(self, dt: datetime) -> str:
        """Convert Gregorian to Haab' - correlation affects this too"""
        jdn = self._datetime_to_julian(dt)
        days_since_creation = jdn - self.julian_ref  # Now varies by correlation
        haab_day = days_since_creation % 365

        if haab_day < 360:
            month_num = haab_day // 20
            day_num = haab_day % 20
            return f"{day_num} {self.haab_months[month_num]}"
        else:
            uayeb_day = haab_day - 360
            return f"{uayeb_day} Uayeb"

    def haab_to_gregorian(self, haab: str, reference_year: int = 2000) -> datetime:
        """Convert Haab' to Gregorian (approximate)"""
        day_str, month = haab.split(' ', 1)
        target_day = int(day_str)

        if month == 'Uayeb':
            target_day += 360  # Uayeb days are 360-364

        ref_jdn = self._datetime_to_julian(datetime(reference_year, 1, 1))
        ref_days_since_creation = ref_jdn - self.julian_ref

        # Calculate target Julian Day
        target_days_since_creation = (ref_days_since_creation // 365) * 365 + target_day
        target_jdn = self.julian_ref + target_days_since_creation

        return self._julian_to_datetime(target_jdn)

    @classmethod
    def long_count_now(cls, correlation: str = 'GMT') -> str:
        """Get current Long Count date"""
        converter = cls(correlation)
        return converter.gregorian_to_long_count(datetime.now())

    @classmethod
    def tzolkin_now(cls, correlation: str = 'GMT') -> str:
        """Get current Tzolkin date"""
        converter = cls(correlation)
        return converter.gregorian_to_tzolkin(datetime.now())

    @classmethod
    def haab_now(cls, correlation: str = 'GMT') -> str:
        """Get current Haab' date"""
        converter = cls(correlation)
        return converter.gregorian_to_haab(datetime.now())
