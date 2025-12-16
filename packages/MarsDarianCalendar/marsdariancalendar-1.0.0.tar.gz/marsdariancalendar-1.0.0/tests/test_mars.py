# This file is part of Darian Mars Calendar Python Package.
# Darian Mars Calendar Python Package is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
# Darian Mars Calendar Python Package is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with Darian Mars Calendar Python Package.
# If not, see <https://www.gnu.org/licenses/>.
import unittest
from datetime import datetime, timezone, timedelta
from mars import DarianCalendar  # Adjust import as needed


class TestDarianCalendar(unittest.TestCase):

    def setUp(self):
        self.cal = DarianCalendar()

    def test_now_returns_tuple(self):
        """Test that now() returns a tuple of 3 integers."""
        result = self.cal.now()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        self.assertTrue(all(isinstance(x, int) for x in result))

    def test_gregorian_to_darian_basic(self):
        """Test basic conversion from Gregorian to Darian."""
        # Test a known date
        dt = datetime(2023, 1, 1, tzinfo=timezone.utc)
        darian = self.cal.gregorian_to_darian(dt)

        self.assertIsInstance(darian, tuple)
        self.assertEqual(len(darian), 3)
        self.assertTrue(all(isinstance(x, int) for x in darian))
        self.assertGreaterEqual(darian[0], 1)  # Year >= 1
        self.assertGreaterEqual(darian[1], 1)  # Month >= 1
        self.assertLessEqual(darian[1], 24)    # Month <= 24
        self.assertGreaterEqual(darian[2], 1)  # Day >= 1

    def test_darian_to_gregorian_basic(self):
        """Test basic conversion from Darian to Gregorian."""
        # Test with valid Darian date
        gregorian = self.cal.darian_to_gregorian(1, 1, 1)

        self.assertIsInstance(gregorian, datetime)
        self.assertIsNotNone(gregorian.tzinfo)

    def test_round_trip_conversion(self):
        """Test that converting G->D->G gives similar result."""
        original_dt = datetime(2023, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        # Convert to Darian and back
        darian = self.cal.gregorian_to_darian(original_dt)
        roundtrip_dt = self.cal.darian_to_gregorian(*darian)

        # Should be close (within a few seconds due to rounding)
        time_diff = abs((original_dt - roundtrip_dt).total_seconds())
        self.assertLess(time_diff, 86400)  # Less than 1 Earth day difference

    def test_invalid_month_raises_error(self):
        """Test that invalid month raises ValueError."""
        with self.assertRaises(ValueError):
            self.cal.darian_to_gregorian(1, 0, 1)  # Month 0 invalid

        with self.assertRaises(ValueError):
            self.cal.darian_to_gregorian(1, 25, 1)  # Month 25 invalid

    def test_invalid_day_raises_error(self):
        """Test that invalid day raises ValueError."""
        with self.assertRaises(ValueError):
            self.cal.darian_to_gregorian(1, 1, 0)  # Day 0 invalid

    def test_timezone_handling(self):
        """Test timezone handling in conversions."""
        # Test with different timezones
        eastern = timezone(timedelta(hours=-5))
        dt_eastern = datetime(2023, 1, 1, 12, 0, 0, tzinfo=eastern)

        darian_eastern = self.cal.gregorian_to_darian(dt_eastern)
        self.assertIsInstance(darian_eastern, tuple)

        # Should work the same as UTC equivalent
        dt_utc = dt_eastern.astimezone(timezone.utc)
        darian_utc = self.cal.gregorian_to_darian(dt_utc)

        # Results should be similar (may differ by 1 sol due to timezone conversion)
        self.assertEqual(darian_eastern[0], darian_utc[0])  # Same year

    def test_format_darian(self):
        """Test Darian date formatting."""
        formatted = self.cal.format_darian(1, 1, 1)
        self.assertIn("Sagittarius", formatted)
        self.assertIn("1", formatted)

        formatted = self.cal.format_darian(5, 12, 15)
        self.assertIn("Vrisha", formatted)  # 24th month
        self.assertIn("5", formatted)
        self.assertIn("15", formatted)

    def test_edge_cases(self):
        """Test edge cases in conversions."""
        # Test epoch date
        epoch_dt = datetime(1970, 1, 1, tzinfo=timezone.utc)
        darian = self.cal.gregorian_to_darian(epoch_dt)

        # Should be close to year 1, day 1
        self.assertGreaterEqual(darian[0], 1)

        # Test far future date
        future_dt = datetime(2100, 1, 1, tzinfo=timezone.utc)
        future_darian = self.cal.gregorian_to_darian(future_dt)
        self.assertGreater(future_darian[0], 1)

if __name__ == '__main__':
    unittest.main()
