import pytest
from unittest.mock import patch, Mock
from datetime import date

from app.api.exceptions import CurrencyNotFoundError, InvalidApiResponseError
from app.api.nbp_client import NBPClient
from app.domain.rate_dto import ExchangeRateDTO


def test_exchange_rate_dto_repr():
    rate = ExchangeRateDTO(date=date(2025, 12, 16), value=3.593)
    assert repr(rate) == "ExchangeRateDTO((2025, 12, 16), 3.593)"

@patch("app.api.nbp_client.requests.get")
def test_get_current_exchange_rate(mock_get):
    mock_response = Mock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "table": "A",
        "currency": "USD",
        "code": "USD",
        "rates": [{"effectiveDate": "2025-12-16", "mid": 3.593}]
    }
    mock_get.return_value = mock_response

    client = NBPClient()
    rate = client.get_current_exchange_rate("USD")

    assert isinstance(rate, ExchangeRateDTO)
    assert rate.date == date(2025, 12, 16)
    assert rate.value == 3.593
    assert repr(rate) == "ExchangeRateDTO((2025, 12, 16), 3.593)"


@patch("app.api.nbp_client.requests.get")
def test_get_currency_rates_for_given_period(mock_get):
    mock_response = Mock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "table": "A",
        "currency": "EUR",
        "code": "EUR",
        "rates": [
            {"effectiveDate": "2025-12-15", "mid": 4.123},
            {"effectiveDate": "2025-12-16", "mid": 4.134}
        ]
    }
    mock_get.return_value = mock_response

    client = NBPClient()
    rates = client.get_currency_rates_for_given_period(
        "EUR", date(2025, 12, 15), date(2025, 12, 16)
    )

    assert len(rates) == 2
    assert all(isinstance(r, ExchangeRateDTO) for r in rates)
    assert rates[0].date == date(2025, 12, 16)
    assert rates[0].value == 4.134
    assert rates[1].date == date(2025, 12, 15)
    assert rates[1].value == 4.123

    assert repr(rates[0]) == "ExchangeRateDTO((2025, 12, 16), 4.134)"


@patch("app.api.nbp_client.requests.get")
def test_currency_not_found_error(mock_get):
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_get.return_value = mock_response

    client = NBPClient()
    with pytest.raises(CurrencyNotFoundError):
        client.get_current_exchange_rate("ABC")

@patch("app.api.nbp_client.requests.get")
def test_server_error(mock_get):
    mock_get.return_value.ok = False
    mock_get.return_value.status_code = 500
    mock_get.return_value.text = "Internal Server Error"

    client = NBPClient()
    import pytest

    with pytest.raises(InvalidApiResponseError) as exc:
        client.get_current_exchange_rate("USD")
    assert "NBP API error 500" in str(exc.value)