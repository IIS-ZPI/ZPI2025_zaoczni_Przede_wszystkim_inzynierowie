import requests
from datetime import date
from .exceptions import (
    CurrencyNotFoundError,
    InvalidApiResponseError
)
from ..domain.rate_dto import ExchangeRateDTO

"""
    Client responsible for communication with the National Bank of Poland (NBP)
    public REST API.

    This class provides methods for retrieving official currency exchange rates
    from NBP exchange rate table A and mapping external API responses into
    domain-specific Data Transfer Objects (DTOs).

    The client handles HTTP communication, response validation, and error
    translation, while remaining independent of any business or analytical logic.
"""

class NBPClient:

    BASE_URL = "https://api.nbp.pl/api"
    TABLE = "A"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            "Accept": "application/json"
        }

    """
       Retrieves a chronological time series of exchange rates for a given currency
       within the specified date range.

       The method queries the NBP REST API (exchange rate table A) and returns
       normalized exchange rate data mapped into immutable domain DTO objects.
       Returned data is sorted in ascending order by publication date.

       Parameters
       ----------
       currency : str
           ISO 4217 three-letter currency code (e.g. "USD", "EUR", "CHF").
       start_date : date
           The beginning date of the requested time range (inclusive).
       end_date : date
           The ending date of the requested time range (inclusive).

       Returns
       -------
       list[ExchangeRateDTO]
           A list of exchange rate DTOs representing the currency exchange rate
           values for consecutive business days within the specified period.
    """

    def get_currency_rates_for_given_period(
        self,
        currency: str,
        start_date: date,
        end_date: date
    ) -> list[ExchangeRateDTO]:

        url = (
            f"{self.BASE_URL}/exchangerates/rates/"
            f"{self.TABLE}/{currency}/"
            f"{start_date}/{end_date}/"
        )

        response = requests.get(url, headers=self.headers, timeout=self.timeout)

        if response.status_code == 404:
            raise CurrencyNotFoundError(
                f"Currency '{currency}' not found in table A or no data for given period."
            )

        if not response.ok:
            raise InvalidApiResponseError(
                f"NBP API error {response.status_code}: {response.text}"
            )

        data = response.json()

        rates = [
            ExchangeRateDTO(
                date=date.fromisoformat(rate["effectiveDate"]),
                value=rate["mid"]
            )
            for rate in data["rates"]
        ]

        rates.sort(key=lambda r: r.date, reverse=True)

        return rates

    """
        Retrieves the most recent exchange rate for a given currency.
    
        The method queries the NBP REST API (exchange rate table A) and returns
        the latest published exchange rate mapped into a domain-specific DTO.
    
        Parameters
        ----------
        currency : str
            ISO 4217 three-letter currency code (e.g. "USD", "EUR", "CHF").
    
        Returns
        -------
        ExchangeRateDTO
            A DTO containing the most recent exchange rate value and its
            publication date.
    """

    def get_current_exchange_rate(
            self,
            currency: str
    ) -> ExchangeRateDTO:

        url = (
            f"{self.BASE_URL}/exchangerates/rates/"
            f"{self.TABLE}/{currency}/"
        )

        response = requests.get(url, headers=self.headers, timeout=self.timeout)

        if response.status_code == 404:
            raise CurrencyNotFoundError(
                f"Currency '{currency}' not found in table A."
            )

        data = response.json()

        return ExchangeRateDTO(
            date=date.fromisoformat(data["rates"][0]["effectiveDate"]),
            value=data["rates"][0]["mid"]
        )
