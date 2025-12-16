# Darian Calendar Converter

A Python library for converting between Gregorian and Darian calendars, designed for Mars timekeeping applications.

## What is the Darian Calendar?

The Darian calendar is a proposed calendar system for Mars, developed by aerospace engineer Thomas Gangale in the 1980s. It divides the Martian year into 24 months with alternating lengths of 27 and 28 sols (Martian days), closely matching Mars' orbital period of approximately 687 Earth days. Each sol is about 24 hours and 39 minutes long.

The calendar is primarily used in scientific research, Mars mission planning, and science fiction to provide a standardized way to track time on Mars. Unlike Earth's calendar, which is based on lunar cycles, the Darian calendar is purely solar-based and designed to accommodate Mars' unique orbital characteristics.

### References

- [Wikipedia: Darian calendar](https://en.wikipedia.org/wiki/Darian_calendar)
- [Scientific article: Mars Time for Mars Surface Operations](https://www.sciencedirect.com/science/article/pii/S0273117710003453)
- [Thomas Gangale's Darian Calendar System](http://www.martian-time.com/)

## Installation

This package uses UV for dependency management:

```bash
# Install with UV
uv pip install MarsDarianCalendar

# Or add to your project
uv add MarsDarianCalendar
```

## Usage
### Basic Conversion
```python
from marsdariancalendar import DarianCalendar
from datetime import datetime, timezone

# Initialize with default UTC timezone
cal = DarianCalendar()

# Convert Gregorian to Darian
gregorian_date = datetime(2023, 6, 15, tzinfo=timezone.utc)
darian_date = cal.gregorian_to_darian(gregorian_date)
print(f"Darian date: {darian_date}")  # (year, month, day)

# Convert Darian to Gregorian
gregorian = cal.darian_to_gregorian(1, 12, 15)
print(f"Gregorian date: {gregorian}")

# Get current Darian date
current_darian = cal.now()
print(f"Current Darian: {current_darian}")

# Format Darian date as string
formatted = cal.format_darian(5, 12, 15)
print(f"Formatted: {formatted}")  # "5 Vrisha 15"
```

### With Custom Timezone
```python
from datetime import timezone, timedelta

# Use Eastern Time
eastern = timezone(timedelta(hours=-5))
cal = DarianCalendar(earth_timezone=eastern)
```
### Features
- Convert between Gregorian and Darian dates
- Support for custom Earth timezones
- Current Darian date retrieval
- Proper date formatting with traditional month names
- Unit tested for accuracy

## Development
```bash
# Clone and setup development environment
uv sync --dev

# Run tests
uv run pytest

# Install additional dev dependencies
uv add --group dev black flake8 mypy
```
