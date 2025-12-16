# Maya Date Converter

A Python library for converting between Gregorian and Mayan calendar systems. Supports all three traditional Mayan calendars: Long Count, Tzolkin, and Haab'.

## 📜 Overview

The Maya civilization developed multiple sophisticated calendar systems that worked together. This library provides accurate conversions between the Gregorian calendar and these three Mayan systems:

### The Three Mayan Calendars

1. __Long Count__
    - A linear count of days from a mythical creation date (August 11, 3114 BCE in the proleptic Gregorian calendar)
    - Format: Baktun.Katun.Tun.Uinal.Kin (e.g., 13.0.12.2.12)
    - Cycle: 5,125 years (13 baktuns)
    - Purpose: Historical and ceremonial dating
    - References:
        - [Wikipedia: Mesoamerican Long Count calendar](https://en.wikipedia.org/wiki/Mesoamerican_Long_Count_calendar)
2. __Tzolkin__ (Divine Calendar)
    - A 260-day sacred calendar combining 13 numbers with 20 day names
    - Cycle: 260 days (13 × 20)
    - Format: Number Name (e.g., 4 Ahau)
    - Purpose: Religious ceremonies, divination, naming
    - References:
        - [Wikipedia: Tzolkin](https://en.wikipedia.org/wiki/Tzolk%CA%BCin)
        - [Time and the Highland Maya - Phd Barbara Tedlock (1992)](https://www.academia.edu/4380893/Barbara_Tedlock_Time_and_the_Highland_Maya_1992)
3. __Haab'__ (Solar Calendar)
    - A 365-day solar calendar similar to our year
    - 18 months of 20 days each plus 5 "nameless" days (Uayeb)
    - Format: Day Month (e.g., 12 Kankin)
    - Purpose: Agricultural and seasonal tracking
    - References:
        - [Wikipedia: Haab (Maya Calendar)](https://en.wikipedia.org/wiki/Haab%CA%BC_(Maya_calendar))
        - [Time and the Highland Maya - Phd Barbara Tedlock (1992)](https://www.academia.edu/4380893/Barbara_Tedlock_Time_and_the_Highland_Maya_1992)

## 📜 Use Cases

### Historical Research

- Convert archaeological dates to Mayan calendar systems
- Analyze historical documents with Mayan dates

### Cultural Studies

- Educational tools for learning about Maya civilization
- Cultural preservation and documentation

### Astronomical Calculations

- Track celestial events in Mayan calendar context
- Study astronomical alignments in ancient sites

### Gaming and Simulation

- Historical simulation games
- Cultural education applications

## 📦 Installation

### Using pip

```bash
pip install MayaCalendar
```

### Using uv (recommended)

```bash
uv pip install MayaCalendar
```

Or add to your project:

```bash
uv add MayaCalendar
```

## 🛠️ Usage Examples

### Basic Conversion

```python
from mayacalendar import MayanDateConverter
from datetime import datetime

# Initialize converter (defaults to GMT correlation)
converter = MayanDateConverter()

# Convert Gregorian to Mayan calendars
date = datetime(2024, 12, 10)
print(f"Long Count: {converter.gregorian_to_long_count(date)}")
print(f"Tzolkin: {converter.gregorian_to_tzolkin(date)}")
print(f"Haab': {converter.gregorian_to_haab(date)}")

# Convert back to Gregorian
long_count = "13.0.12.2.12"
gregorian_date = converter.long_count_to_gregorian(long_count)
print(f"Back to Gregorian: {gregorian_date}")
```

### Using Different Correlations

```python
# GMT (Goodman-Martinez-Thompson) correlation (default)
gmt_converter = MayanDateConverter('GMT')

# Spinden correlation (2 days later)
spinden_converter = MayanDateConverter('Spinden')

date = datetime(2024, 1, 1)
gmt_result = gmt_converter.gregorian_to_long_count(date)
spinden_result = spinden_converter.gregorian_to_long_count(date)

print(f"GMT: {gmt_result}")
print(f"Spinden: {spinden_result}")  # Will be 2 days earlier
```

### Getting Current Mayan Dates

```python
from mayacalendar import MayanDateConverter

# Current dates using class methods
print(f"Today's Long Count: {MayanDateConverter.long_count_now()}")
print(f"Today's Tzolkin: {MayanDateConverter.tzolkin_now()}")
print(f"Today's Haab': {MayanDateConverter.haab_now()}")

# With specific correlation
print(f"GMT Today: {MayanDateConverter.long_count_now('GMT')}")
print(f"Spinden Today: {MayanDateConverter.long_count_now('Spinden')}")
```

### Correlation Systems

The Mayan calendar system requires a correlation to convert to the Gregorian calendar. This library supports two main systems:

#### Goodman-Martinez-Thompson (GMT) - Default

- Most widely accepted by scholars
- Reference: August 11, 3114 BCE = 0.0.0.0.0
- Julian Day Number: 584283
- Used by virtually all modern Mayanists

#### Spinden Correlation

- Alternative system proposed in the 1930s
- 2 days later than GMT
- Julian Day Number: 584285
- Less commonly used but historically significant

## 🛠️ API Reference

### Constructor

```python
converter = MayanDateConverter(correlation='GMT')  # 'GMT' or 'Spinden'
```

### Conversion Methods

- `gregorian_to_long_count(dt)` - Convert datetime to Long Count string
- `gregorian_to_tzolkin(dt)` - Convert datetime to Tzolkin string
- `gregorian_to_haab(dt)` - Convert datetime to Haab' string
- `long_count_to_gregorian(long_count)` - Convert Long Count to datetime
- `tzolkin_to_gregorian(tzolkin, reference_year=2000)` - Convert Tzolkin to datetime
- `haab_to_gregorian(haab, reference_year=2000)` - Convert Haab' to datetime

### Class Methods (get current date)

- `MayanDateConverter.long_count_now(correlation='GMT')`
- `MayanDateConverter.tzolkin_now(correlation='GMT')`
- `MayanDateConverter.haab_now(correlation='GMT')`

## ⚖️ [Licence GNU GPLv3](./LICENSE)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
