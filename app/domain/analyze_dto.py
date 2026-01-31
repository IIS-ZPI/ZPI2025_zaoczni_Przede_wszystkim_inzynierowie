from dataclasses import dataclass
from datetime import date
from typing import Dict, List

"""
    Data Transfer Object (DTO) representing the result of a statistical
    analysis of a currency's exchange rates over a specified period.

    This immutable object is designed to safely transfer calculated
    metrics between the API layer (NBPClient) and the business logic layer
    without risk of accidental modification.

    Attributes
    ----------
    currency : str
        The 3-letter ISO 4217 currency code (e.g., "USD", "EUR").
    start_date : date
        The first date in the analyzed period.
    end_date : date
        The last date in the analyzed period.
    median : float
        The median of the exchange rates during the period.
    modes : float | list[float]
        The most frequent exchange rate(s) during the period. If all rates
        occur only once, this is an empty list.
    std_dev : float
        The standard deviation of the exchange rates.
    coefficient_of_variation : float
        The relative measure of dispersion: std_dev divided by the mean.
    sessions : Dict[str, int]
        A dictionary counting session types:
            - "increased": number of sessions where the rate increased
            - "decreased": number of sessions where the rate decreased
            - "unchanged": number of sessions where the rate stayed the same
"""

@dataclass(frozen=True)
class AnalyzeDTO:
    currency: str
    start_date: date
    end_date: date
    median: float
    modes: List[float]
    std_dev: float
    coefficient_of_variation: float
    sessions: Dict[str, int]

    def __repr__(self):
        return (f"AnalyzeDTO(currency={self.currency}, "
                f"start_date={self.start_date}, end_date={self.end_date}, "
                f"median={self.median}, modes={self.modes}, "
                f"std_dev={self.std_dev}, coeff_var={self.coefficient_of_variation}, "
                f"sessions={self.sessions})")