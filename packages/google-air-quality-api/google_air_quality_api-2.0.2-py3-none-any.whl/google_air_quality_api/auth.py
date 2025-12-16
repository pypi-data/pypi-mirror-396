"""API for Google Air Quality OAuth.

Callers subclass this to provide an asyncio implementation that refreshes
authentication tokens.
"""

import logging
from http import HTTPStatus
from typing import Any, TypeVar

import aiohttp
from aiohttp.client_exceptions import ClientError
from mashumaro.mixins.json import DataClassJSONMixin

from .const import API_BASE_URL
from .exceptions import (
    ApiError,
    ApiForbiddenError,
    AuthError,
    NoDataForLocationError,
)
from .model import Error, ErrorResponse

_LOGGER = logging.getLogger(__name__)


MALFORMED_RESPONSE = "Server returned malformed response"
ERROR_CONNECTING = "Error connecting to API"

_T = TypeVar("_T", bound=DataClassJSONMixin)


class Auth:
    """Base class for Google Air Quality authentication library.

    Provides an asyncio interface around the blocking client library.
    """

    def __init__(
        self,
        websession: aiohttp.ClientSession,
        api_key: str,
        *,
        host: str | None = None,
        referrer: str | None = None,
    ) -> None:
        """Initialize the auth."""
        self._websession = websession
        self._host = host or API_BASE_URL
        self.api_key = api_key
        self.referrer = referrer

    async def request(
        self,
        method: str,
        url: str,
        headers: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> aiohttp.ClientResponse:
        """Make a request."""
        if headers is None:
            headers = {}
        if self.referrer:
            headers["Referer"] = self.referrer
        if not url.startswith(("http://", "https://")):
            url = f"{self._host}/{url}"
        _LOGGER.debug("request[%s]=%s %s", method, url, kwargs)
        if method != "get" and "json" in kwargs:
            _LOGGER.debug("request[post json]=%s", kwargs["json"])
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}key={self.api_key}"

        return await self._websession.request(method, url, **kwargs, headers=headers)

    async def get(self, url: str, **kwargs: Any) -> aiohttp.ClientResponse:
        """Make a get request."""
        try:
            resp = await self.request("get", url, **kwargs)
        except ClientError as err:
            raise ApiError(err) from err
        return await Auth._raise_for_status(resp)

    async def get_json(
        self,
        url: str,
        data_cls: type[_T],
        **kwargs: Any,
    ) -> _T:
        """Make a get request and return json response."""
        resp = await self.get(url, **kwargs)
        try:
            result = await resp.text()
        except ClientError as err:
            message = f"{ERROR_CONNECTING}: {err}"
            raise ApiError(message) from err
        _LOGGER.debug("response=%s", result)
        try:
            return data_cls.from_json(result)
        except (LookupError, ValueError) as err:
            message = f"{MALFORMED_RESPONSE}: {err}"
            raise ApiError(message) from err

    async def post(self, url: str, **kwargs: Any) -> aiohttp.ClientResponse:
        """Make a post request."""
        try:
            resp = await self.request("post", url, **kwargs)
        except ClientError as err:
            message = f"{ERROR_CONNECTING}: {err}"
            raise ApiError(message) from err
        return await Auth._raise_for_status(resp)

    async def post_json(self, url: str, data_cls: type[_T], **kwargs: Any) -> _T:
        """Make a post request and return a json response."""
        resp = await self.post(url, **kwargs)
        try:
            result = await resp.text()
        except ClientError as err:
            message = f"{ERROR_CONNECTING}: {err}"
            raise ApiError(message) from err
        _LOGGER.debug("response=%s", result)
        try:
            return data_cls.from_json(result)
        except (LookupError, ValueError) as err:
            message = f"{MALFORMED_RESPONSE}: {err}"
            raise ApiError(message) from err

    @classmethod
    async def _raise_for_status(
        cls, resp: aiohttp.ClientResponse
    ) -> aiohttp.ClientResponse:
        """Raise exceptions on failure methods."""
        error_detail = await cls._error_detail(resp)
        try:
            resp.raise_for_status()
        except aiohttp.ClientResponseError as err:
            error_message = f"{err.message} response from API ({resp.status})"
            if error_detail:
                error_message += f": {error_detail}"
                if "Information is unavailable for this location" in error_message:
                    raise NoDataForLocationError(error_message) from err
            if err.status == HTTPStatus.FORBIDDEN:
                raise ApiForbiddenError(error_message) from err
            if err.status == HTTPStatus.UNAUTHORIZED:
                raise AuthError(error_message) from err
            raise ApiError(error_message) from err
        except aiohttp.ClientError as err:
            message = f"Error from API: {err}"
            raise ApiError(message) from err
        return resp

    @classmethod
    async def _error_detail(cls, resp: aiohttp.ClientResponse) -> Error | None:
        """Return an error message string from the API response."""
        if resp.status < 400:
            return None
        try:
            result = await resp.text()
        except ClientError:
            return None
        try:
            error_response = ErrorResponse.from_json(result)
        except (LookupError, ValueError):
            return None
        return error_response.error
