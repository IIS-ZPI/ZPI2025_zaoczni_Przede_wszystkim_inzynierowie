from __future__ import annotations
from datetime import date, datetime
from typing import List, Tuple
import math

from app.api.nbp_client import NBPClient
from app.domain.rate_dto import ExchangeRateDTO
from app.domain.distribution_dto import DistributionDTO
from app.error.exceptions import InvalidDateRangeError
from app.util.period_calculator import PeriodCalculator

"""
    Service class responsible for calculating the distribution of changes
    for a currency pair (FR-05) and displaying it as an ASCII histogram.
"""


class DistributionService:

    def __init__(self, nbp_client: NBPClient):
        self.nbp_client = nbp_client

    def calculate_distribution(
            self,
            currency_1: str,
            currency_2: str,
            period: str,
            start: str | None
    ) -> DistributionDTO:

        end_date = (
            datetime.strptime(start, "%Y-%m-%d").date()
            if start
            else date.today()
        )
        start_date = PeriodCalculator.calculate_start_date(end_date, period)

        rates_1 = self._get_rates_or_pln(currency_1, start_date, end_date)
        rates_2 = self._get_rates_or_pln(currency_2, start_date, end_date)

        pair_rates = self._calculate_pair_rates(rates_1, rates_2)

        if len(pair_rates) < 2:
            raise InvalidDateRangeError("Not enough aligned data points to calculate changes.")

        changes = []
        for i in range(1, len(pair_rates)):
            change = pair_rates[i] - pair_rates[i - 1]
            changes.append(change)

        return DistributionDTO(
            currency_pair=f"{currency_1}/{currency_2}",
            start_date=start_date,
            end_date=end_date,
            changes=changes
        )

    def display_histogram(self, dto: DistributionDTO) -> None:
        """
        Generates and prints a vertical ASCII histogram (pyramid-like structure)
        as required by SRS FR-05.
        """
        changes = dto.changes
        if not changes:
            print("No data to display.")
            return

        print(f"\nDistribution for {dto.currency_pair} ({dto.start_date} - {dto.end_date})")
        print("Y-axis: Frequency (days) | X-axis: Change bins")
        print("-" * 70)

        # --- 1. Dynamic Configuration (Bins) ---
        days_diff = (dto.end_date - dto.start_date).days

        if days_diff < 45:  # ~1 month
            num_bins = 7
        elif days_diff < 100:  # ~1 quarter
            num_bins = 12
        else:  # 6 months / 1 year
            num_bins = 18

        min_val = min(changes)
        max_val = max(changes)

        if max_val == min_val:
            bin_width = 1.0
        else:
            bin_width = (max_val - min_val) / num_bins

        # --- 2. Bucketize Data ---
        bins_counts = [0] * num_bins
        bin_ranges = []
        for i in range(num_bins):
            low = min_val + i * bin_width
            high = min_val + (i + 1) * bin_width
            bin_ranges.append((low, high))

        for val in changes:
            if val == max_val:
                idx = num_bins - 1
            else:
                idx = int((val - min_val) / bin_width)
                idx = min(idx, num_bins - 1)
                idx = max(idx, 0)
            bins_counts[idx] += 1

        # --- 3. Draw Vertical Histogram ---
        max_freq = max(bins_counts) if bins_counts else 0

        for row in range(max_freq, 0, -1):
            line = f"{row:>3} | "

            for count in bins_counts:
                if count >= row:
                    line += " #### "
                else:
                    line += "      "
            print(line)

        # --- 4. Draw X-axis ---
        # Padding "    " aligns the '+' with the '|' above
        print("    " + "+-----" * num_bins + "+")

        # --- 5. Draw Bin Indices ---
        labels_line = "     "
        for i in range(num_bins):
            labels_line += f" ({i + 1:<2}) "
        print(labels_line)
        print("-" * 70)

        # --- 6. Print Legend ---
        try:
            unit = dto.currency_pair.split('/')[1]
        except:
            unit = "PLN"

        print(f"Legend (Ranges in {unit}):")
        half = (num_bins + 1) // 2
        for i in range(half):
            r1_low, r1_high = bin_ranges[i]
            col1 = f"({i + 1:<2}): [{r1_low:+.4f}, {r1_high:+.4f})"

            if i + half < num_bins:
                r2_low, r2_high = bin_ranges[i + half]
                col2 = f"({i + half + 1:<2}): [{r2_low:+.4f}, {r2_high:+.4f})"
                print(f"{col1:<35} | {col2}")
            else:
                print(f"{col1}")

    # --- Helper Methods ---
    def _get_rates_or_pln(self, currency: str, start: date, end: date) -> List[ExchangeRateDTO]:
        if currency.upper() == 'PLN':
            return []

        rates = []
        date_ranges = PeriodCalculator.split_date_range(start, end)
        for r_start, r_end in date_ranges:
            rates.extend(self.nbp_client.get_currency_rates_for_given_period(currency, r_start, r_end))

        rates.sort(key=lambda r: r.date)
        return rates

    def _calculate_pair_rates(self, rates_a: List[ExchangeRateDTO], rates_b: List[ExchangeRateDTO]) -> List[float]:
        if rates_a and rates_b:
            dict_a = {r.date: r.value for r in rates_a}
            dict_b = {r.date: r.value for r in rates_b}
            common_dates = sorted(list(set(dict_a.keys()) & set(dict_b.keys())))
            return [dict_a[d] / dict_b[d] for d in common_dates]

        elif not rates_a and rates_b:
            return [1.0 / r.value for r in rates_b]

        elif rates_a and not rates_b:
            return [r.value / 1.0 for r in rates_a]
