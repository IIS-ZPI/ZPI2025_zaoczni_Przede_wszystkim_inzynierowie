from dataclasses import dataclass
from datetime import date

"""
    Data Transfer Object (DTO) representing a single currency exchange rate
    published by the National Bank of Poland.

    This object is used to transfer normalized exchange rate data between
    the API communication layer and the business logic layer of the system.
    It is intentionally immutable to ensure data integrity and to prevent
    accidental modification of external data during statistical analysis.

    Attributes
    ----------
    date : date
        The publication date of the exchange rate (business day).
    value : float
        The exchange rate value (mid rate) expressed in PLN, retrieved
        from NBP exchange rate table A.
"""

@dataclass(frozen=True)
class ExchangeRateDTO:
    date: date
    value: float

    def __repr__(self):
        return f"ExchangeRateDTO(({self.date.year}, {self.date.month}, {self.date.day}), {self.value})"
