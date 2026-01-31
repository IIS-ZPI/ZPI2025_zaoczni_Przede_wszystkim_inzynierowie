from datetime import date, timedelta


class MockRate:
    """
    Independent currency rate mock.
    Simulates ExchangeRateDTO but allows easy date manipulation via offsets.
    """

    def __init__(self, value: float, day_offset: int):
        self.value = value
        # Start date is January 1st, 2024 + offset days
        self.date = date(2024, 1, 1) + timedelta(days=day_offset)


class MyMockNBPClient:
    """
    Independent API client mock.
    Allows manual data injection (set_data) without network calls.
    """

    def __init__(self):
        self.usd_rates = []
        self.eur_rates = []

    def set_data(self, currency: str, rates: list[float]):
        """Helper method to load test data."""
        mock_objects = [MockRate(val, i) for i, val in enumerate(rates)]

        if currency == "USD":
            self.usd_rates = mock_objects
        elif currency == "EUR":
            self.eur_rates = mock_objects

    def get_currency_rates_for_given_period(self, currency, start_date, end_date):
        if currency == "USD":
            return self.usd_rates
        elif currency == "EUR":
            return self.eur_rates
        return []