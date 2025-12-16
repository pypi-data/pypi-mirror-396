"""Exceptions for Google Air Quality API calls."""


class GoogleAirQualityApiError(Exception):
    """Error talking to the Google Air Quality API."""


class ApiError(GoogleAirQualityApiError):
    """Raised during problems talking to the API."""


class AuthError(GoogleAirQualityApiError):
    """Raised due to auth problems talking to API."""


class ApiForbiddenError(GoogleAirQualityApiError):
    """Raised due to permission errors talking to API."""


class NoDataForLocationError(GoogleAirQualityApiError):
    """Raised due to permission errors talking to API."""
