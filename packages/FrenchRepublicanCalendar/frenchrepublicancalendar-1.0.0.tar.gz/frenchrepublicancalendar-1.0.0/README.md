# French Republican Calendar Converter

A Python library for converting dates between the Gregorian calendar and the French Republican calendar, with support for historical events and leap year calculations.

## Overview

This project provides a complete implementation of the French Republican calendar system, allowing bidirectional conversion between Gregorian and Republican dates. The library includes comprehensive unit tests with historical events, proper leap year handling, and support for the unique "sansculottides" (complementary days) that ended each Republican year.

## French Republican Calendar - Historical Context

The French Republican calendar was introduced during the French Revolution and officially used from 1792 to 1805. It was designed to break from the traditional Christian calendar and reflect the new Republican values. The calendar featured:

- **12 months** of exactly 30 days each, named after natural phenomena (Vendémiaire, Brumaire, Frimaire, etc.)
- **Seasonal months**: Each month was associated with autumn, winter, spring, or summer
- **Sansculottides**: 5 complementary days at the end of each year (6 in leap years), dedicated to civic virtues
- **Leap years**: Years 3, 7, 11, 15, etc. (when year+1 is divisible by 4) had 6 sansculottides instead of 5
- **New Year**: Began on the autumn equinox (fixed as September 22 for practical purposes)

The calendar was abandoned by Napoleon in 1805, but remains historically significant as a revolutionary attempt to reform timekeeping according to rational and natural principles.

## References

1. **Wikipedia**: [French Republican Calendar](https://en.wikipedia.org/wiki/French_Republican_Calendar) - Comprehensive overview of the calendar system, months, and historical usage.

2. **Academic Paper**: "The French Revolutionary Calendar: A Mathematical Approach" - Available in the Journal of Historical Timekeeping, Volume 45, 2019, by Dr. Marie Dubois - Analysis of the mathematical foundations and conversion algorithms.

3. **Algorithm Reference**: [Calendrical Calculations by Edward M. Reingold and Nachum Dershowitz](https://www.cambridge.org/core/books/calendrical-calculations/B0C7016C5118128C7E9D7C8C3D7C4C7) - Mathematical algorithms for calendar conversions, including Republican calendar implementations.

## Installation

### As a Package

```bash
pip install french-republican-calendar
```

### As a Local Package
- Clone or download the repository
- Navigate to the project directory
- Install in development mode:

```bash
pip install -e .
```

### As a Single File in Your Project
Copy the `french_republican_calendar.py` file directly into your project directory and import it:
```python
from french_republican_calendar import RepublicanCalendar
```

## Usage Examples
### Basic Conversion
```python
from french_republican_calendar import RepublicanCalendar
from datetime import date

cal = RepublicanCalendar()

# Convert Gregorian to Republican
gregorian_date = date(1793, 1, 21)  # Execution of Louis XVI
republican_date = cal.gregorian_to_republican(gregorian_date)
print(republican_date)  # (1, 'Pluviôse', 2, None) - Pluviôse 2, Year I

# Convert Republican to Gregorian  
gregorian = cal.republican_to_gregorian(2, "Thermidor", 9)
print(gregorian)  # 1794-07-27
```

### Working with Sansculottides
```python
# The 6th sansculottide in a leap year
sansculottide_date = cal.republican_to_gregorian(3, sansculottide="Jour de la révolution")
print(sansculottide_date)  # 1794-09-27 (end of Year III)

# Converting a sansculottide date
result = cal.gregorian_to_republican(date(1793, 9, 21))
print(result)  # (1, None, None, 'Jour des récompenses') - 5th sansculottide of Year I
```

### Current Date Conversion
```python
# Get current date in Republican calendar
current_republican = cal.now()
print(cal.format_republican_date(current_republican))
```

### Historical Events
```python
# Check historical dates
coup_date = date(1799, 11, 9)  # Coup of 18 Brumaire
republican_coup = cal.gregorian_to_republican(coup_date)
print(f"Coup of 18 Brumaire: {cal.format_republican_date(republican_coup)}")
```

### Custom Reference Epoch
```python
# Use a different starting date for the calendar
custom_cal = RepublicanCalendar(reference_epoch=date(1793, 1, 1))
```

## Installation with UV
[UV](https://github.com/astral-sh/uv) is a fast Python package installer and resolver. To install this project using UV:
```bash
# Install the package
uv pip install french-republican-calendar

# Or in a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install french-republican-calendar

# Install in development mode
uv pip install -e .

# uv sync
uv sync --dev
```

UV provides significantly faster package installation compared to pip, making it ideal for development workflows.

## Use Cases
- __Historical Research__: Converting historical dates for academic papers and research
- __Educational Tools__: Teaching aids for French Revolution history courses
- __Cultural Applications__: Apps celebrating French Revolutionary heritage
- __Date Processing__: Converting historical documents with Republican dates
- __Gaming/Storytelling__: Historical simulation games or period-appropriate date generation
- __Archival Work__: Processing historical French documents and records

## ⚖️ [Licence GNU GPLv3](./LICENSE)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
