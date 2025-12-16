"""Pure Python implementation of the mayacalendar module."""

__all__ = ("MayaDate")

__name__ = "mayacalendar"

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
__version__ = "2.0.0"
__last_modified_on__ = "2025-12-13"


def _get_class_module(self):
    module_name = self.__class__.__module__
    if module_name == 'mayacalendar':
        return 'mayacalendar.'
    else:
        return ''


class MayaDate:
    """A Python library to manage MayaDate, and for converting between Gregorian (datetime object) and Mayan calendar systems.
    Supports all three traditional Mayan calendars: Long Count, Tzolkin, and Haab'.

    # Overview

    The Maya civilization developed multiple sophisticated calendar systems that worked together.
    This library provides accurate conversions between the Gregorian calendar and these three Mayan systems:

    ## The Three Mayan Calendars:

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

    ## Correlation Systems

    The Mayan calendar system requires a correlation to convert to the Gregorian calendar. This library supports two main systems:

    ### Goodman-Martinez-Thompson (GMT) - Default

    - Most widely accepted by scholars
    - Reference: August 11, 3114 BCE = 0.0.0.0.0
    - Julian Day Number: 584283
    - Used by virtually all modern Mayanists

    ### Spinden Correlation

    - Alternative system proposed in the 1930s
    - 2 days later than GMT
    - Julian Day Number: 584285
    - Less commonly used but historically significant
    """

    def __new__(
        cls,
        datetime: datetime = None,
        long_count: str = None,
        tzolkin: str = None,
        haab: str = None,
        reference_year: int = 2000,
        correlation: str = 'GMT',
    ):
        """MayaDate

        Args:
            datetime (datetime, optional): datetime. Defaults to None.
            long_count (str, optional): Maya Long Count date. Defaults to None.
            tzolkin (str, optional): Maya Tzolkin date. Defaults to None.
            haab (str, optional): Maya Haab' date. Defaults to None.
            reference_year (int, optional): Reference_year, in which approximate year to convert a Tzolkin or Haab' date. Defaults to 2000.
            correlation (str, optional): Correlation. Defaults to 'GMT', other option 'Spinden'.
                                         (ref to MayaDate general documentation for more details on the Correlation Systems)

        Raises:
            ValueError: Invalid submitted data warning.

        Returns:
            MayaDate: MayaDate Object
        """
        self = object.__new__(cls)
        self.correlation = correlation
        self.__correlations = {
            'GMT': 584283,  # Julian Day for Aug 11, 3114 BCE
            'Spinden': 584285  # Alternative correlation (2 days later)
        }
        self._correlation_ref = self.__correlations.get(self.correlation, 584283)
        self.julian_ref = self.__correlations.get(self.correlation, 584283)
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
        if sum(x is not None for x in [datetime, long_count, tzolkin, haab]) >= 2:
            raise ValueError('At most one of datetime, long_count, tzolkin, or haab can be provided.')
        elif datetime and not long_count and not tzolkin and not haab:
            # Datetime (Build From)
            self._datetime = datetime
            self.long_count = self.gregorian_to_long_count(datetime)
            self.tzolkin = self.gregorian_to_tzolkin(datetime)
            self.haab = self.gregorian_to_haab(datetime)
        elif not datetime and long_count and not tzolkin and not haab:
            # Long Count (Build From)
            self._datetime = self.long_count_to_gregorian(long_count)
            self.long_count = long_count.strip()
            self.tzolkin = self.gregorian_to_tzolkin(self._datetime)
            self.haab = self.gregorian_to_haab(self._datetime)
        elif not datetime and not long_count and tzolkin and not haab:
            # Tzolkin (Build From)
            self._datetime = self.tzolkin_to_gregorian(tzolkin=tzolkin.title(), reference_year=reference_year)
            self.long_count = self.gregorian_to_long_count(self._datetime)
            self.tzolkin = tzolkin.strip().title()
            self.haab = self.gregorian_to_haab(self._datetime)
        elif not datetime and not long_count and not tzolkin and haab:
            # Haab (Build From)
            self._datetime = self.haab_to_gregorian(haab=haab.title(), reference_year=reference_year)
            self.long_count = self.gregorian_to_long_count(self._datetime)
            self.tzolkin = self.gregorian_to_tzolkin(self._datetime)
            self.haab = haab.strip().title()
        else:
            # Neutral (Everything Empty)
            self._datetime = None
            self.long_count = None
            self.tzolkin = None
            self.haab = None
        return self

    def _datetime_to_julian(self, dt: datetime) -> int:
        """Convert datetime to Julian Day Number

        Args:
            dt (datetime): datetime

        Returns:
            int: Julian Date Number
        """
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        return dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045

    def _julian_to_datetime(self, jdn: int) -> datetime:
        """Convert Julian Day Number back to datetime

        Args:
            jdn (int): Julian Date Number

        Returns:
            datetime: datetime
        """
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
        """Convert Gregorian/standard datetime to Long Count, uses correlation.
        (ref to MayaDate general documentation for more details on the Correlation Systems)

        Args:
            dt (datetime): datetime

        Returns:
            str:  Long Count Date (e.g.: '12.19.7.9.11')
        """
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
        """Convert Long Count to Gregorian/standard datetime, uses correlation.
        (ref to MayaDate general documentation for more details on the Correlation Systems)

        Expl: '12.19.7.9.11'
        MayaDate.long_count_to_gregorian('12.19.7.9.11')

        Args:
            long_count (str): Long Count Date

        Raises:
            ValueError: _description_

        Returns:
            datetime: datetime
        """
        try:
            baktun, katun, tun, uinal, kin = map(int, long_count.strip().split('.'))
            total_days = baktun * 144000 + katun * 7200 + tun * 360 + uinal * 20 + kin
            jdn = self.julian_ref + total_days  # This now varies by correlation
            return self._julian_to_datetime(jdn)
        except ValueError:
            raise ValueError(f'Invalid Long Count date submitted. You submitted "{long_count}", \
this method expect "baktun.katun.tun.uinal.kin", as strings of `int` separated by a `.` (dot), such as "int.int.int.int.int". \
For instance "12.19.7.9.11", "13.0.13.3.0", etc.')

    def gregorian_to_tzolkin(self, dt: datetime) -> str:
        """Convert Gregorian/standard datetime to Tzolkin, uses correlation.
        (ref to MayaDate general documentation for more details on the Correlation Systems)

        Args:
            dt (datetime): datetime

        Returns:
            str: Tzolkin date (e.g.: '4 Muluc')
        """
        jdn = self._datetime_to_julian(dt)
        days_since_creation = jdn - self.julian_ref  # Now varies by correlation
        tzolkin_num = ((days_since_creation + 8) % 13) + 1  # Starting from 9 Ik
        tzolkin_name_idx = (days_since_creation + 8) % 20
        return f"{tzolkin_num} {self.tzolkin_names[tzolkin_name_idx]}"

    def tzolkin_to_gregorian(self, tzolkin: str, reference_year: int = 2000) -> datetime:
        """Convert Tzolkin to Gregorian/standard datetime, approximate within reference year range (Default: 2000). Uses correlation.
        (ref to MayaDate general documentation for more details on the Correlation Systems)

        Expl: '4 Muluc'
        MayaDate.tzolkin_to_gregorian('4 Muluc')

        Args:
            tzolkin (str): Tzolkin date
            reference_year (int, optional): reference_year. Defaults to 2000.

        Raises:
            ValueError: _description_

        Returns:
            datetime: datetime
        """
        try:
            num_str, name = tzolkin.strip().split(' ', 1)
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
        except ValueError:
            raise ValueError(f'Invalid Tzolkin date submitted. You submitted "{tzolkin}" (reference_year: {reference_year}), \
this method expect str(tzolkin_num:int, tzolkin_name:str), using one of the Tzolkin Months: {self.tzolkin_names}.')

    def gregorian_to_haab(self, dt: datetime) -> str:
        """Convert Gregorian/standard datetime to Haab', uses correlation.
        (ref to MayaDate general documentation for more details on the Correlation Systems)

        Args:
            dt (datetime): datetime

        Returns:
            str: Maya Haab' Date (e.g.: '11 Chen')
        """
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
        """Convert Haab' to Gregorian/standard datetime, approximate within reference year range (Default: 2000). Uses correlation.
        (ref to MayaDate general documentation for more details on the Correlation Systems)

        Expl: '11 Chen'
        MayaDate.haab_to_gregorian('11 Chen')


        Args:
            haab (str): Haab' date
            reference_year (int, optional): reference_year. Defaults to 2000.

        Raises:
            ValueError: _description_

        Returns:
            datetime: datetime
        """
        try:
            day_str, month = haab.strip().split(' ', 1)
            target_day = int(day_str)
            if month not in self.haab_months:
                raise ValueError

            if month == 'Uayeb':
                target_day += 360  # Uayeb days are 360-364

            # Not Sure this is computed correctly to translate a Haab' date -- Needs Double Check
            ref_jdn = self._datetime_to_julian(datetime(reference_year, 1, 1))
            ref_days_since_creation = ref_jdn - self.julian_ref

            # Calculate target Julian Day
            target_days_since_creation = (ref_days_since_creation // 365) * 365 + target_day
            target_jdn = self.julian_ref + target_days_since_creation

            return self._julian_to_datetime(target_jdn)
        except ValueError:
            raise ValueError(f'Invalid Haab\' date submitted. You submitted "{haab}" (reference_year: {reference_year}), \
this method expect str(haab_num:int, haab_name:str), using one of the Haab\' Months: {self.haab_months}.')

    def __repr__(self):
        """Convert to formal string, for repr().

        >>> d = MayaDate(datetime.datetime(2025, 12, 13))
        >>> repr(d)
        'mayacalendar.MayaDate(13.0.13.3.0, 4 Muluc, 15 Kankin, , GMT, 584283, 2025-12-13 00:00:00.000)'
        # Or
        >>> lc = MayaDate(long_count='13.0.13.3.1')
        >>> repr(lc)
        'mayacalendar.MayaDate(13.0.13.3.1, 5 Oc, 16 Kankin, 584283, GMT, 2025-12-14 00:00:00)'
        """
        return "%s%s(%s, %s, %s, %d, %s, %s)" % (
                                        _get_class_module(self),
                                        self.__class__.__qualname__,
                                        self.long_count,
                                        self.tzolkin,
                                        self.haab,
                                        self._correlation_ref,
                                        self.correlation,
                                        self._datetime,
                                    )

    def __str__(self) -> str:
        """Convert to string, for str().

        >>> print(MayaDate(datetime.datetime(2025, 12, 13)))
        Maya Date - Long Count: 13.0.13.3.0, Tzolkin: 4 Muluc, Haab: 15 Kankin, Correlation: (GMT) 584283 \
(Gregorian Datetime: 2025-12-13 00:00:00.000)
        """
        return f"Maya Date - Long Count: {self._long_count}, Tzolkin: {self._tzolkin}, Haab: {self._haab}, \
Correlation: ({self.correlation}) {self._correlation_ref} (Gregorian Datetime: {self._datetime})"

    @classmethod
    def long_count_now(cls, correlation: str = 'GMT') -> str:
        """Get current Long Count date.
        (ref to MayaDate general documentation for more details on the Correlation Systems)

        Args:
            correlation (str, optional): Correlation. Defaults to 'GMT'.

        Returns:
            str: Maya Long Count date. (expl: 13.0.13.3.0)
        """
        converter = cls(correlation=correlation)
        return converter.gregorian_to_long_count(datetime.now())

    @classmethod
    def tzolkin_now(cls, correlation: str = 'GMT') -> str:
        """Get current Tzolkin date.
        (ref to MayaDate general documentation for more details on the Correlation Systems)

        Args:
            correlation (str, optional): Correlation. Defaults to 'GMT'.

        Returns:
            str: Maya Tzolkin date. (expl: 4 Muluc)
        """
        converter = cls(correlation=correlation)
        return converter.gregorian_to_tzolkin(datetime.now())

    @classmethod
    def haab_now(cls, correlation: str = 'GMT') -> str:
        """Get current Haab' date.
        (ref to MayaDate general documentation for more details on the Correlation Systems)

        Args:
            correlation (str, optional): Correlation. Defaults to 'GMT'.

        Returns:
            str: Maya Haab' date. (expl: 15 Kankin)
        """
        converter = cls(correlation=correlation)
        return converter.gregorian_to_haab(datetime.now())

    @classmethod
    def now(cls, correlation: str = 'GMT') -> str:
        """Get current Long Count, Tzolkin and Haab' date, as a MayaDate object.
        (ref to MayaDate general documentation for more details on the Correlation Systems)

        Args:
            correlation (str, optional): Correlation. Defaults to 'GMT'.

        Returns:
            MayaDate (obj): MayaDate Object at datetime.now().
        """
        return cls(datetime=datetime.now(), correlation=correlation)
