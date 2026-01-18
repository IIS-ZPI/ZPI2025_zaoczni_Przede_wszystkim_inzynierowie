class NBPApiError(Exception):
    """Base exception for NBP API errors"""


class CurrencyNotFoundError(NBPApiError):
    pass


class NoDataForDateRangeError(NBPApiError):
    pass


class InvalidApiResponseError(NBPApiError):
    pass