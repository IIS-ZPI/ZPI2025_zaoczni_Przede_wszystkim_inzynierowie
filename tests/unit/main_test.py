import pytest
from unittest.mock import patch, MagicMock
from datetime import date

# Import functions from your main.py
from app.main import validate_date, main


# ==========================================
# DATE VALIDATION TESTS
# ==========================================

def test_validate_date_valid():
    """Verifies that a correct date string is converted to a date object."""
    dt = validate_date("2023-05-01")
    assert dt == date(2023, 5, 1)


def test_validate_date_empty_returns_today():
    """Verifies that empty input returns today's date."""
    assert validate_date(None) == date.today()


def test_validate_date_future_throws_error():
    """Verifies that a future date raises a ValueError."""
    # Ensure we pick a date definitely in the future
    future_year = date.today().year + 1
    with pytest.raises(ValueError, match="cannot be in the future"):
        validate_date(f"{future_year}-01-01")


def test_validate_date_too_old_throws_error():
    """Verifies that a date before 2002 raises a ValueError."""
    with pytest.raises(ValueError, match="supported NBP archival range"):
        validate_date("1990-01-01")


def test_validate_date_invalid_format():
    """Verifies that garbage input raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid date format"):
        validate_date("not-a-date")


# ==========================================
# MAIN LOOP & COMMAND ROUTING TESTS
# ==========================================

@patch('builtins.input')  # Mocks user input
@patch('builtins.print')  # Mocks console output (to keep test clean)
@patch('app.main.NBPClient')  # Mocks API connection
def test_main_prevents_same_currency(mock_client, mock_print, mock_input):
    """
    Verifies that comparing the same currency (USD vs USD) triggers an error
    and does NOT call the service.
    """
    # Simulate user typing a bad command, then exiting
    mock_input.side_effect = [
        "change-distribution USD USD --period 1-month",
        "exit"
    ]

    # Run main loop (it will process inputs and finish at 'exit')
    try:
        main()
    except SystemExit:
        pass

    # Collect all print calls to check for the error message
    # We join all printed arguments into one long string
    printed_text = " ".join(
        [str(call.args[0]) for call in mock_print.call_args_list if call.args]
    )

    assert "Currency pair must consist of two different currencies" in printed_text


@patch('builtins.input')
@patch('builtins.print')
@patch('app.main.DistributionService')  # Mock the class, not instance
@patch('app.main.NBPClient')
def test_main_routes_to_distribution_service(mock_client, mock_service_class, mock_print, mock_input):
    """
    Verifies that a valid command correctly initializes the service
    and calls its methods.
    """
    # Simulate valid command -> exit
    mock_input.side_effect = [
        "change-distribution USD EUR --period 1-month --start 2024-01-01",
        "exit"
    ]

    # Setup the mock service instance
    mock_service_instance = mock_service_class.return_value
    # Mock calculation result
    mock_service_instance.calculate_distribution.return_value = "FakeDTO"

    try:
        main()
    except SystemExit:
        pass

    # 1. Check if Service was initialized
    mock_service_class.assert_called_once()

    # 2. Check if calculation was called with correct args
    mock_service_instance.calculate_distribution.assert_called_once()
    call_kwargs = mock_service_instance.calculate_distribution.call_args.kwargs

    assert call_kwargs['currency_1'] == 'USD'
    assert call_kwargs['currency_2'] == 'EUR'
    assert call_kwargs['period'] == '1-month'

    # 3. Check if display was called
    mock_service_instance.display_histogram.assert_called_once_with("FakeDTO")