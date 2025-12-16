# This file is part of Darian Mars Calendar Python Package.
# Darian Mars Calendar Python Package is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
# Darian Mars Calendar Python Package is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with Darian Mars Calendar Python Package.
# If not, see <https://www.gnu.org/licenses/>.
from datetime import datetime, timezone, timedelta

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


class DarianCalendar:
    def __init__(self, earth_timezone=timezone.utc):
        self.earth_timezone = earth_timezone
        # Mars prime meridian (Airy-0) is used as reference (like Earth's UTC)
        self.mars_timezone = timezone.utc  # Mars equivalent of UTC

    def gregorian_to_darian(self, dt):
        """Convert Gregorian datetime to Darian date."""
        # Convert to UTC if not already
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=self.earth_timezone)
        else:
            dt = dt.astimezone(timezone.utc)

        # Reference epoch: January 1, 1970 (Unix epoch)
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)

        # Calculate elapsed time since epoch
        elapsed = dt - epoch
        total_seconds = elapsed.total_seconds()

        # Mars day (sol) = 88775.244 seconds (24h 39m 35.244s)
        mars_day_seconds = 24*3600 + 39*60 + 35.244
        sols_since_epoch = total_seconds / mars_day_seconds

        # Darian calendar calculations
        # Each Mars year = ~668.5921 sols
        mars_year = int(sols_since_epoch // 668.5921) + 1
        day_of_year = int(sols_since_epoch % 668.5921)

        # 24 months in Darian calendar, alternating 27/28 sols
        # First 12 months: 6 months of 28 sols, 6 months of 27 sols
        # Last 12 months: reverse pattern
        month_lengths = [28, 27, 28, 27, 28, 27, 28, 27, 28, 27, 28, 27,
                         27, 28, 27, 28, 27, 28, 27, 28, 27, 28, 27, 28]

        day_counter = day_of_year
        month = 0
        for i, length in enumerate(month_lengths):
            if day_counter < length:
                month = i + 1
                day = day_counter + 1
                break
            day_counter -= length

        return mars_year, month, day

    def darian_to_gregorian(self, darian_year, darian_month, darian_day):
        """Convert Darian date to Gregorian datetime."""
        # Validate input
        if darian_month < 1 or darian_month > 24:
            raise ValueError("Darian month must be 1-24")
        if darian_day < 1:
            raise ValueError("Darian day must be positive")

        # Calculate day of year
        month_lengths = [28, 27, 28, 27, 28, 27, 28, 27, 28, 27, 28, 27,
                        27, 28, 27, 28, 27, 28, 27, 28, 27, 28, 27, 28]

        day_of_year = sum(month_lengths[:darian_month-1]) + (darian_day - 1)

        # Calculate total sols since epoch
        mars_year = darian_year - 1  # Adjust for 1-indexed years
        total_sols = mars_year * 668.5921 + day_of_year

        # Convert to Earth seconds
        mars_day_seconds = 24*3600 + 39*60 + 35.244
        total_seconds = total_sols * mars_day_seconds

        # Convert to datetime
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
        result = epoch + timedelta(seconds=total_seconds)

        return result.astimezone(self.earth_timezone)

    def now(self):
        """Get current Darian date."""
        now_gregorian = datetime.now(self.earth_timezone)
        return self.gregorian_to_darian(now_gregorian)

    def format_darian(self, darian_year, darian_month, darian_day):
        """Format Darian date as string."""
        month_names = [
            "Sagittarius", "Dhanus", "Capricornus", "Makara", "Aquarius", "Kumbha",
            "Pisces", "Mina", "Aries", "Mesha", "Taurus", "Vrisha",
            "Gemini", "Mithuna", "Cancer", "Karka", "Leo", "Simha",
            "Virgo", "Kanya", "Libra", "Tula", "Scorpius", "Vrishika"
        ]

        if 1 <= darian_month <= 24:
            month_name = month_names[darian_month - 1]
        else:
            month_name = f"Month {darian_month}"

        return f"{darian_year} {month_name} {darian_day}"
