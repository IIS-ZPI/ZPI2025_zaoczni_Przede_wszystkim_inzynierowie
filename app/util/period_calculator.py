from datetime import date, timedelta
import calendar

MAX_DAYS = 93

"""
   Utility class for calculating date ranges based on predefined periods
   for currency exchange rate analysis.

   This class provides methods to:
       - Compute the start date given an end date and a period (week, month, quarter, etc.)
       - Split a long date range into chunks that respect the NBP API limit (MAX_DAYS = 93)
       - Handle month and year arithmetic safely (e.g., varying month lengths, leap years)
"""

class PeriodCalculator:

    """
       Calculates the start date of a period relative to a given end date.

       Parameters
       ----------
       end_date : date
           The anchor date (usually the end of the analysis period).
       period : str
           One of the supported periods:
               - '1-week'
               - '2-weeks'
               - '1-month'
               - '1-quarter'
               - '6-months'
               - '1-year'

       Returns
       -------
       date
           The computed start date corresponding to the specified period.
    """

    @staticmethod
    def calculate_start_date(
        end_date: date,
        period: str
    ) -> date:
        start_date = None

        if period == "1-week":
            start_date = end_date - timedelta(weeks=1)
        elif period == "2-weeks":
            start_date = end_date - timedelta(weeks=2)
        elif period == "1-month":
            start_date = PeriodCalculator._subtract_months(end_date, 1)
        elif period == "1-quarter":
            start_date = PeriodCalculator._subtract_months(end_date, 3)
        elif period == "6-months":
            start_date = PeriodCalculator._subtract_months(end_date, 6)
        elif period == "1-year":
            start_date = PeriodCalculator._subtract_years(end_date, 1)
        else:
            raise ValueError(f"Unsupported period: {period}")

        # Ensure start date is not before NBP data limit (2002-01-02)
        min_allowed_date = date(2002, 1, 2)
        if start_date < min_allowed_date:
            return min_allowed_date

        return start_date

    """
        Subtracts a given number of months from a date, handling year rollover
        and adjusting the day if the resulting month has fewer days.

        Parameters
        ----------
        d : date
            The original date.
        months : int
            Number of months to subtract.

        Returns
        -------
        date
            The resulting date after subtracting months.
    """

    @staticmethod
    def _subtract_months(d: date, months: int) -> date:
        year = d.year
        month = d.month - months

        while month <= 0:
            month += 12
            year -= 1

        last_day = calendar.monthrange(year, month)[1]
        day = min(d.day, last_day)

        return date(year, month, day)

    """
        Subtracts a given number of years from a date, handling leap years.

           If the original date is February 29 and the resulting year is not
           a leap year, adjusts the date to February 28.

           Parameters
           ----------
           d : date
               The original date.
           years : int
               Number of years to subtract.

           Returns
           -------
           date
               The resulting date after subtracting years.
    """

    @staticmethod
    def _subtract_years(d: date, years: int) -> date:
        try:
            return d.replace(year=d.year - years)
        except ValueError:
            return d.replace(month=2, day=28, year=d.year - years)

    """
        Splits a long date range into smaller subranges, each of maximum
        length MAX_DAYS, to comply with the NBP API limit on requests.

        Parameters
        ----------
        start : date
            The start date of the full range.
        end : date
            The end date of the full range.
    """

    def split_date_range(start: date, end: date) -> list[tuple[date, date]]:
        ranges = []
        current_start = start

        while current_start <= end:
            current_end = min(
                current_start + timedelta(days=MAX_DAYS - 1),
                end
            )
            ranges.append((current_start, current_end))
            current_start = current_end + timedelta(days=1)

        return ranges