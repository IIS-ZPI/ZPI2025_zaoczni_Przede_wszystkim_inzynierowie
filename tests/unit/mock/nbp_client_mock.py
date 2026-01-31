from tests.unit.mock.exchange_rate_mock import FakeRate


class MockNBPClient:
    def get_currency_rates_for_given_period(self, currency, start_date, end_date):
        rates = [4.00, 4.11, 4.05, 4.05, 4.07, 4.15, 4.10, 4.12, 4.05, 4.08]
        return [FakeRate(r) for r in rates]

class MockNBPClientNoMode:
    def get_currency_rates_for_given_period(self, currency, start_date, end_date):
        rates = [4.01, 4.03, 4.05, 4.07, 4.09, 4.11, 4.13, 4.15, 4.17, 4.19]
        return [FakeRate(r) for r in rates]

class MockNBPClientSingleValue:
    def get_currency_rates_for_given_period(self, currency, start_date, end_date):
        return [FakeRate(4.00)]