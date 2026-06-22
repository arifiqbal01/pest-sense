class WeatherProviderError(Exception):
    """Base weather provider error."""


class WeatherProviderRequestError(WeatherProviderError):
    """HTTP/network failure."""


class WeatherProviderResponseError(WeatherProviderError):
    """Malformed provider response."""