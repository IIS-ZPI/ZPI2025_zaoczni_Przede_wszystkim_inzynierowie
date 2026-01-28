from dataclasses import dataclass
from datetime import date
from typing import List

"""
    Data Transfer Object (DTO) for distribution analysis.

    Stores RAW changes (List[float]) instead of pre-calculated bins.
    This allows the display layer to dynamically generate the ASCII histogram.

    Attributes
    ----------
    currency_pair : str
        The formatted currency pair (e.g., "EUR/USD").
    start_date : date
        Start of the analysis period.
    end_date : date
        End of the analysis period.
    changes : List[float]
        A list of daily changes (difference between current and previous day rate).
"""


@dataclass(frozen=True)
class DistributionDTO:
    currency_pair: str
    start_date: date
    end_date: date
    changes: List[float]