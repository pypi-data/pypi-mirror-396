"""Public exceptions."""
import corehttp.exceptions
from enum import Enum
from typing import Tuple, Dict, Any, Union
import re
from lseg_analytics.core.common import AsyncRequestResponse, AsyncPollingResponse

__all__ = ["LibraryException", "ServerError", "ResourceNotFound", "GatewayError", "AuthenticationError", "ProxyStatusError", "ProxyNotEnabledError", "ProxyAuthFailureError","ProxyNotFoundError",
           "BadRequestError"]


class _ERROR_MESSAGE(Enum):
    PROXY_DISABLED = "Cannot connect to the LSEG Financial Analytics platform because seamless authentication is not enabled. Please enable it in the LSEG Analytics extension settings in your IDE and try again."
    PROXY_UNAUTHORIZED = "Cannot connect to the LSEG Financial Analytics platform because you are not logged in to the extension. Please log in, and try again."
    PROXY_FORBIDDEN = "Cannot connect to the LSEG Financial Analytics platform because you are not authorized to the extension. Please contact the LSEG support team."
    NO_AVALIABLE_PORT = "Cannot connect to the LSEG Financial Analytics platform because the port number to enable seamless authentication was not found. Please try restarting VS Code or contact the LSEG support team if the problem persists."
    INVALID_RESPONSE = "Cannot connect to the LSEG Financial Analytics platform because there is an error with seamless authentication and the status of the extension cannot be retrieved. Please try restarting VS Code or contact the LSEG support team if the problem persists."
    CREDENTIAL_UNAUTHORIZED = "Cannot authenticate to the LSEG Financial Analytics platform. Please ensure your client id/password is configured correctly."
    GET_TOKEN_FAILED = "Cannot connect to the LSEG Financial Analytics platform because of a network or certification issue. Please check your network connection."
    PROXY_FAILURE = "Cannot connect to the LSEG Financial Analytics platform because there was an error with seamless authentication. Please try restarting VS Code or contact the LSEG support team if the problem persists."


class LibraryException(Exception):
    """Base class for all library exception, excluding azure ones"""

class ServerError(LibraryException):
    """Server error exception"""

class ProxyStatusError(LibraryException):
    """Proxy failed exception"""

class ProxyNotEnabledError(LibraryException):
    """Proxy not enabled exception"""

class ProxyNotFoundError(LibraryException):
    """Proxy not found exception"""    

class ProxyAuthFailureError(LibraryException):
    """Proxy authentication or authorization exception"""        

class ResourceNotFound(ServerError):
    """Resource not found exception"""


class GatewayError(LibraryException):
    """Gateway error exception"""


class AuthenticationError(GatewayError):
    """Authentication error exception"""


class BadRequestError(LibraryException):
    """Bad request error exception"""


def check_exception_and_raise(error, logger):
    """Check exception and raise appropriate error"""
    wrapped_error = error
    if isinstance(error, corehttp.exceptions.ServiceRequestError):
        logger.error(f"{error}")
        wrapped_error = AuthenticationError(
            f"Cannot connect to the LSEG Financial Analytics platform because of a network or certification issue({error}). Please check your network connection."
        )
    if isinstance(error, corehttp.exceptions.HttpResponseError):
        error_status, error_code, error_message = _extract_error_details(error)
        # (ASDK-688)
        if isinstance(error, corehttp.exceptions.DecodeError) and error.status_code == 504:
            wrapped_error = ServerError(f"Server error: {error}")
        elif error_message.startswith("API Gateway -") or error_message.startswith("Azure WAF Error -"):  # Gateway error
            wrapped_error = GatewayError(f"Gateway error: code={error_code} {error_message}")
        elif str(error_status).lower() in [ "not found", "404"]:
            wrapped_error = ResourceNotFound(f"Resource not found: code={error_code} {error_message}")
        elif str(error_status).lower() in [ "bad request", "400"]:
            wrapped_error = BadRequestError(f"Bad request: code={error_code} {error_message}")
        else:
            wrapped_error = ServerError(f"Server error: code={error_code} {error_message}")
    logger.error(f"Exception: {wrapped_error}")
    raise wrapped_error from None


def _extract_error_details(error: corehttp.exceptions.HttpResponseError) -> Tuple[str, str, str]:
    """Extract error status, code, and message from HttpResponseError"""
    error_status = error.status_code or "Unknown error code"
    error_code = error_status
    error_message = error.message

    if hasattr(error.response, "_json") and error.response._json:
        json_error = error.response._json
        if "error" in json_error: # LFA error
            error_status = json_error["error"].get("status", error_status)
            error_code = json_error["error"].get("code", error_code)
            error_message = json_error["error"].get("message", error_message)
        else: # YB or other errors
            error_message = f"{json_error}"

    return error_status, error_code, _sanitize_response_tokens(error_message)


def check_id(id):
    """Check if id is None"""
    if id is None:
        raise LibraryException("Resource should be saved first before calling the method!")


def _sanitize_response_tokens(response_str: str) -> str:
    """
    Remove JWT tokens from response string using regex pattern matching.

    Args:
        response_str (str): String representation of the response object

    Returns:
        str: Sanitized response string with tokens replaced
    """
    # JWT token pattern: header.payload.signature (base64url encoded parts separated by dots)
    # Each part is base64url: [A-Za-z0-9_-]+ (no padding = signs in middle, may have at end)
    # This pattern is from Semgrep Rule Id: detected-jwt-token
    jwt_pattern = r"eyJ[A-Za-z0-9-_=]{14,}\.[A-Za-z0-9-_=]{13,}\.?[A-Za-z0-9-_.+/=]*?"

    # Replace any JWT tokens
    sanitized = re.sub(jwt_pattern, "[REDACTED]", response_str)

    return sanitized


def check_async_polling_response(response: Union[Tuple[Any, Dict[str, str]], Any]) -> AsyncPollingResponse:
    """
    Check async polling response and return structured AsyncPollingResponse.

    Args:
        response: A tuple containing (body, headers) for async polling if not complete, or a direct response object if complete

    Returns:
        AsyncPollingResponse: Structured response with polling information

    Raises:
        LibraryException: If response format is unexpected or invalid
    """

    # 202 response (in progress)
    if isinstance(response, tuple):
        if len(response) != 2:
            raise LibraryException(
                f"Unexpected tuple length for polling response: " f"expected 2 elements, got {len(response)}"
            )
        body, headers = response

        return AsyncPollingResponse(
            status=body.status,
            location=headers.get("location"),
            retry_after=headers.get("retry-after"),
            response=None,
        )

    # Validate body structure
    if not all(hasattr(response, attr) for attr in ["status", "response"]):
        raise ServerError("Invalid body response from async polling 200 response: missing required attributes")

    # 200 response (completed)
    return AsyncPollingResponse(
        status=response.status,
        location=None,
        retry_after=None,
        response=response.response.data,
    )


def check_async_request_response(response: Union[Tuple[Any, Dict[str, str]], Any]) -> Union[AsyncRequestResponse, Any]:
    """
    Check async request response and return appropriate response object.

    Args:
        response: Either a tuple (body, headers) for 202 responses (async in progress)
                 or direct response object for 200 responses (completed)

    Returns:
        AsyncRequestResponse: For 202 responses with polling information
        Any: Response data for completed 200 responses

    Raises:
        LibraryException: If response format is unexpected or invalid
    """
    if isinstance(response, tuple):  # 202 response
        if len(response) != 2:
            raise LibraryException(
                f"Unexpected tuple length for async request response: " f"expected 2 elements, got {len(response)}"
            )
        body, headers = response
        return AsyncRequestResponse(
            status=body.status,
            location=headers.get("location"),
            retry_after=headers.get("retry-after"),
            operation_id=headers.get("x-ap-requestid"),
        )

    # This is a 200 response (completed) - return the data directly
    if hasattr(response, "data"):
        return response.data
    else:
        raise ServerError(
            f"Unexpected response type for async request: expected data attribute, got {type(response).__name__}"
        )
