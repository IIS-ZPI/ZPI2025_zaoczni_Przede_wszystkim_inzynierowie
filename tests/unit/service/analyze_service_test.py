import pytest
from datetime import date

from app.services.analyze_service import CurrencyAnalysisService
from app.domain.analyze_dto import AnalyzeDTO
from app.error.exceptions import InvalidDateRangeError

from tests.unit.mock.nbp_client_mock import (
    MockNBPClient,
    MockNBPClientNoMode,
    MockNBPClientSingleValue,
)

def test_analyze_command_returns_analyze_dto():
    service = CurrencyAnalysisService(MockNBPClient())

    result = service.analyze_command(
        currency="usd",
        period="1-week",
        start="2024-01-10"
    )

    assert isinstance(result, AnalyzeDTO)
    assert result.currency == "USD"
    assert result.start_date < result.end_date

def test_median_calculation():
    service = CurrencyAnalysisService(MockNBPClient())

    result = service.analyze_command(
        currency="EUR",
        period="1-week",
        start="2024-01-10"
    )

    assert result.median == 4.075

def test_mode_detected():
    service = CurrencyAnalysisService(MockNBPClient())

    result = service.analyze_command(
        currency="EUR",
        period="1-week",
        start="2024-01-10"
    )

    assert result.modes == [4.05]

def test_no_mode_when_all_values_unique():
    service = CurrencyAnalysisService(MockNBPClientNoMode())

    result = service.analyze_command(
        currency="USD",
        period="1-week",
        start="2024-01-10"
    )

    assert result.modes == []

def test_standard_deviation_and_coefficient_positive():
    service = CurrencyAnalysisService(MockNBPClient())

    result = service.analyze_command(
        currency="CHF",
        period="1-week",
        start="2024-01-10"
    )

    assert result.std_dev > 0
    assert result.coefficient_of_variation > 0

def test_session_counts():
    service = CurrencyAnalysisService(MockNBPClient())

    result = service.analyze_command(
        currency="USD",
        period="1-week",
        start="2024-01-10"
    )

    assert result.sessions["increased"] == 5
    assert result.sessions["decreased"] == 3
    assert result.sessions["unchanged"] == 1

def test_raises_error_when_only_one_rate():
    service = CurrencyAnalysisService(MockNBPClientSingleValue())

    with pytest.raises(InvalidDateRangeError):
        service.analyze_command(
            currency="USD",
            period="1-week",
            start="2024-01-10"
        )

def test_start_none_defaults_to_today():
    service = CurrencyAnalysisService(MockNBPClient())

    result = service.analyze_command(
        currency="USD",
        period="1-week",
        start=None
    )

    assert isinstance(result.end_date, date)
    assert result.end_date == date.today()
