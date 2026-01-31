import pytest
from datetime import date

from app.services.distribution_service import DistributionService
from app.domain.distribution_dto import DistributionDTO
from app.error.exceptions import InvalidDateRangeError

from tests.unit.mock.distribution_mocks import MyMockNBPClient


def test_calculate_distribution_simple_change():
    """Verifies if the exchange rate difference is calculated correctly for two currencies."""
    client = MyMockNBPClient()
    client.set_data("USD", [4.0, 4.4])
    client.set_data("EUR", [2.0, 2.0])

    service = DistributionService(client)

    result = service.calculate_distribution("USD", "EUR", "1-week", "2024-01-10")

    assert isinstance(result, DistributionDTO)
    assert result.currency_pair == "USD/EUR"
    assert len(result.changes) == 1
    # 2.2 - 2.0 = 0.2
    assert result.changes[0] == pytest.approx(0.2)


def test_calculate_distribution_with_pln():
    """Verifies behavior when the second currency is PLN (which is not in the API)."""
    client = MyMockNBPClient()
    client.set_data("USD", [4.0, 4.1])

    service = DistributionService(client)

    result = service.calculate_distribution("USD", "PLN", "1-week", "2024-01-10")

    assert result.currency_pair == "USD/PLN"
    # (4.1/1.0) - (4.0/1.0) = 0.1
    assert result.changes[0] == pytest.approx(0.1)


def test_calculate_distribution_not_enough_data():
    """Verifies that an error is raised when there is insufficient data (e.g., 1 day)."""
    client = MyMockNBPClient()
    client.set_data("USD", [4.0])
    client.set_data("EUR", [3.5])

    service = DistributionService(client)

    with pytest.raises(InvalidDateRangeError):
        service.calculate_distribution("USD", "EUR", "1-week", "2024-01-10")


def test_display_histogram_output_structure(capsys):
    """
    Verifies if display_histogram actually prints the ASCII chart.
    Uses 'capsys' to capture stdout.
    """
    client = MyMockNBPClient()
    service = DistributionService(client)

    start = date(2024, 1, 1)
    end = date(2024, 1, 10)
    fake_changes = [0.1, 0.1, 0.1]

    dto = DistributionDTO(
        currency_pair="TEST/PAIR",
        start_date=start,
        end_date=end,
        changes=fake_changes
    )

    service.display_histogram(dto)

    captured = capsys.readouterr()
    output = captured.out

    assert "Distribution for TEST/PAIR" in output
    assert "Y-axis: Frequency (days)" in output
    assert "Legend (Ranges in PAIR)" in output
    assert "####" in output
    assert "+-----+" in output


def test_display_histogram_no_data(capsys):
    """Verifies message when changes list is empty."""
    service = DistributionService(MyMockNBPClient())

    dto = DistributionDTO("A/B", date(2024, 1, 1), date(2024, 1, 2), changes=[])

    service.display_histogram(dto)

    captured = capsys.readouterr()
    assert "No data to display." in captured.out


def test_display_histogram_dynamic_bins_quarter(capsys):
    """Verifies if more bars are drawn for a quarterly period (long duration)."""
    service = DistributionService(MyMockNBPClient())

    # Set dates 90 days apart -> should force 12 bins
    start = date(2024, 1, 1)
    end = date(2024, 4, 1)
    dto = DistributionDTO("A/B", start, end, changes=[0.1, 0.2])

    service.display_histogram(dto)

    captured = capsys.readouterr()
    # Check if the last index (12) appears in the legend
    assert "(12)" in captured.out