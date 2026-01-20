from __future__ import annotations

from datetime import date, datetime
from statistics import mean, median, variance, stdev
from collections import Counter

from app.api.nbp_client import NBPClient
from app.domain.analyze_dto import AnalyzeDTO
from app.error.exceptions import InvalidDateRangeError

from app.util.period_calculator import PeriodCalculator

"""
   Service class responsible for performing statistical analysis on
   currency exchange rates retrieved from the National Bank of Poland (NBP).

   This class acts as the business logic layer between the API client (NBPClient)
   and the presentation or CLI layer. It calculates various statistical measures
   and session counts for a user-selected currency over a specified period.

   Attributes
   ----------
   nbp_client : NBPClient
       An instance of the API client used to fetch exchange rate data.
"""

class CurrencyAnalysisService:

    def __init__(self, nbp_client: NBPClient):
        self.nbp_client = nbp_client

    """
        Performs statistical analysis for the specified currency over a given period.

        The method performs the following steps:
        1. Determines the end date for the analysis (anchor date). If no start date is
           provided, uses the current system date.
        2. Calculates the start date based on the requested period (e.g., 1-week,
           1-month, 1-year) using PeriodCalculator.
        3. Splits the date range into chunks that comply with the NBP API maximum
           request length (93 days) to avoid API errors.
        4. Fetches exchange rate data for each chunk via NBPClient and aggregates it.
        5. Validates that there are at least two data points; otherwise, raises
           InvalidDateRangeError.
        6. Computes statistical measures:
            - median: middle value of the exchange rates
            - mode(s): most frequent exchange rate(s)
            - standard deviation: variability of the rates
            - coefficient of variation: relative dispersion (std_dev / mean)
        7. Counts session types by comparing consecutive rates:
            - increased: current rate > previous rate
            - decreased: current rate < previous rate
            - unchanged: current rate == previous rate
        8. Returns an immutable AnalyzeDTO containing all computed metrics.

        Parameters
        ----------
        currency : str
            ISO 4217 3-letter currency code (e.g., "USD", "EUR").
        period : str
            Predefined analysis period ('1-week', '2-weeks', '1-month',
            '1-quarter', '6-months', '1-year').
        start : str | None
            Anchor date in 'YYYY-MM-DD' format. If None, defaults to today.

        Returns
        -------
        AnalyzeDTO
            An immutable object containing:
            - currency code
            - start and end dates of analysis
            - median, mode(s), standard deviation, coefficient of variation
            - session counts (increased, decreased, unchanged)
    """

    def analyze_command(
        self,
        currency: str,
        period: str,
        start: str | None
    ) -> AnalyzeDTO:

        end_date = (
            datetime.strptime(start, "%Y-%m-%d").date()
            if start
            else date.today()
        )

        start_date = PeriodCalculator.calculate_start_date(
            end_date=end_date,
            period=period
        )

        rates = []

        date_ranges = PeriodCalculator.split_date_range(start_date, end_date)

        for range_start, range_end in date_ranges:
            partial_rates = self.nbp_client.get_currency_rates_for_given_period(
                currency=currency,
                start_date=range_start,
                end_date=range_end
            )
            rates.extend(partial_rates)

        if len(rates) < 2:
            raise InvalidDateRangeError(
                "Not enough exchange rate data for analysis."
            )

        values = [r.value for r in rates]


        med = median(values)

        freq = Counter(values)
        max_freq = max(freq.values())

        if max_freq == 1:
            modes = []
        else:
            modes = [v for v, c in freq.items() if c == max_freq]

        std = stdev(values)

        avg = mean(values)
        coeff_var = std / avg

        increases = decreases = unchanged = 0

        for prev, curr in zip(values, values[1:]):
            if curr > prev:
                increases += 1
            elif curr < prev:
                decreases += 1
            else:
                unchanged += 1

        return AnalyzeDTO(
            currency=currency.upper(),
            start_date=start_date,
            end_date=end_date,
            median=med,
            modes=modes,
            std_dev=std,
            coefficient_of_variation=coeff_var,
            sessions={
                "increased": increases,
                "decreased": decreases,
                "unchanged": unchanged
            }
        )

    """
         Displays the results of a currency exchange rate analysis in a clear and readable format.
    
         This method takes an AnalyzeDTO object containing all computed statistical measures
         and session counts, and prints them to the console in a structured way.
    
         The output includes:
             - Currency code (ISO 4217)
             - Analysis period (start date to end date)
             - Median exchange rate
             - Mode(s) of the rates (most frequent values)
             - Standard deviation
             - Coefficient of variation
             - Number of sessions where the rate increased, decreased, or remained unchanged
     """

    def display_analysis(self, analysis: AnalyzeDTO) -> None:

        print(f"Currency: {analysis.currency}")
        print(f"Period: {analysis.start_date} - {analysis.end_date}")
        print(f"Median: {analysis.median}")
        if analysis.modes:
            print(f"Mode: {analysis.modes}")
        else:
            print("Mode: No dominant value")
        print(f"Standard deviation: {analysis.std_dev}")
        print(f"coefficient_of_variation: {analysis.coefficient_of_variation}")
        print(f"Increased: {analysis.sessions['increased']}")
        print(f"Decreased: {analysis.sessions['decreased']}")
        print(f"Unchanged: {analysis.sessions['unchanged']}")

