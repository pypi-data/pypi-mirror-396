from typing import Dict, List, Any
from requests import HTTPError, Response
from urllib.parse import urlparse, parse_qs
from functools import reduce
import json


def _extract_error_message(response: Response) -> str:
    """
    Extract error message from response content.

    :param response: The HTTP response object
    :return: Extracted error message or default message
    """
    try:
        # Try to get error message from JSON response
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            return str(data.get("error"))

        # Try to get error message from text content
        if response.text and response.text.strip():
            # If it's a short text response, use it directly
            if len(response.text.strip()) < 500:
                return response.text.strip()

    except (json.JSONDecodeError, ValueError, KeyError):
        # If JSON parsing fails or no error field found, continue to default
        pass

    return ""


class CoinMetricsClientNotFoundError(Exception):
    """Raised when a CoinMetricsClient instance is not found."""
    def __init__(self, message="CoinMetricsClient not found"):
        self.message = message
        super().__init__(self.message)


class CoinMetricsClientBadParameterError(HTTPError):
    """
    Raised when a request is made with bad parameters (HTTP 400).
    """
    def __init__(self, response: Response, *args: Any, **kwargs: Any):
        if response.status_code != 400:
            response.raise_for_status()
        self.response = response
        self.request = response.request
        error_message = "Bad Parameter: The request contains invalid parameters. API message:\n"
        error_message += _extract_error_message(response)
        self.msg = error_message
        super().__init__(response=response, request=response.request, *args, **kwargs)

    def __str__(self) -> str:
        return self.msg


class CoinMetricsClientUnauthorizedError(HTTPError):
    """
    Raised when a request is unauthorized due to invalid or missing API key (HTTP 401).
    """
    def __init__(self, response: Response, *args: Any, **kwargs: Any):
        if response.status_code != 401:
            response.raise_for_status()
        self.response = response
        self.request = response.request
        error_message = "Unauthorized: The API key is invalid or missing. API message:\n"
        error_message += _extract_error_message(response)
        self.msg = error_message
        super().__init__(response=response, request=response.request, *args, **kwargs)

    def __str__(self) -> str:
        return self.msg


class CoinMetricsClientForbiddenError(HTTPError):
    """
    Raised when a request is forbidden due to insufficient permissions (HTTP 403).
    """
    def __init__(self, response: Response, *args: Any, **kwargs: Any):
        if response.status_code != 403:
            response.raise_for_status()
        self.response = response
        self.request = response.request
        error_message = "Forbidden: The API key does not have permission to access this resource. API message:\n"
        error_message += _extract_error_message(response)
        self.msg = error_message
        super().__init__(response=response, request=response.request, *args, **kwargs)

    def __str__(self) -> str:
        return self.msg


class CoinMetricsClientQueryParamsException(HTTPError):
    """
    Raised when a request is too long.
    """
    def __init__(self, response: Response, *args: Any, **kwargs: Any):
        if response.status_code != 414:
            response.raise_for_status()
        parsed_query_params: Dict[str, List[str]] = parse_qs(
            str(urlparse(url=response.request.url).query)
        )
        get_sum_of_lengths = lambda strings: reduce(lambda a, b: a + len(b), strings, 0)
        param_length_dict = {"Total characters": 0}
        for param, values in parsed_query_params.items():
            sum_of_param_lengths = get_sum_of_lengths(values)
            param_length_dict[param] = sum_of_param_lengths
            param_length_dict["Total characters"] += sum_of_param_lengths
        exception_message = (
            "This request failed because the request URL is too long, consider reducing the length of parameters or using .parallel() to split the request into smaller requests."
            f"\n 414 errors may get returned as total characters in query params exceed 5000"
            f"\nLength of the params provided for reference:\n {param_length_dict}"
        )
        self.msg = exception_message
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return self.msg


class CoinMetricsClientRateLimitError(HTTPError):
    """
    Raised when the rate limit is exceeded (HTTP 429).
    """
    def __init__(self, response: Response, *args: Any, **kwargs: Any):
        if response.status_code != 429:
            response.raise_for_status()
        self.response = response
        self.request = response.request
        self.rate_limit_remaining = response.headers.get("x-ratelimit-remaining", "0")
        self.rate_limit_reset = response.headers.get("x-ratelimit-reset", "0")

        # Extract additional error message from response
        error_message = f"Rate Limit Exceeded: Too many requests. Remaining: {self.rate_limit_remaining}, Reset in: {self.rate_limit_reset} seconds. "
        error_message += _extract_error_message(response)
        error_message += "\nSee https://docs.coinmetrics.io/api/v4/#tag/Rate-limits for more information."

        self.msg = error_message
        super().__init__(response=response, request=response.request, *args, **kwargs)

    def __str__(self) -> str:
        return self.msg


class CoinMetricsClientConnectionError(Exception):
    """
    Raised when a connection error occurs (ConnectionResetError, ChunkedEncodingError).
    """
    def __init__(self, original_error: Exception, *args: Any, **kwargs: Any):
        self.original_error = original_error
        error_message = f"Connection Error: {type(original_error).__name__}: {str(original_error)}"
        self.msg = error_message
        super().__init__(error_message, *args, **kwargs)

    def __str__(self) -> str:
        return self.msg
