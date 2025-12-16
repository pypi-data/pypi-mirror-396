from typing import Generic, TypeVar, Optional
from ._utils import main_object_repr

T = TypeVar("T")


class AsyncRequestResponse:
    """
    Response object for asynchronous request operations (202 responses).

    This class represents the initial response when an async operation is started,
    containing the necessary information for polling the operation status.

    Attributes:
        status: the status of an asynchronous request operation
        location: URL endpoint for polling the operation status
        retry_after: Suggested delay before next polling attempt
        operation_id: Unique identifier for tracking the async request
    """

    def __init__(
        self,
        status: str,
        location: str,
        operation_id: str,
        retry_after: Optional[int] = None,
    ):
        self.status = status
        self.location = location
        self.retry_after = retry_after
        self.operation_id = operation_id


class AsyncPollingResponse(Generic[T]):
    """
    Response object for asynchronous polling operations.

    This class represents the response from polling an async operation,
    which can be either in-progress (202) or completed (200).

    Attributes:
        status: the status of an asynchronous polling operation
        location: URL endpoint for continued polling (if still in progress). None if completed
        retry_after: Suggested delay before next polling attempt. None if completed
        response: The actual response data (present when operation is complete). None if in-progress
    """

    def __init__(
        self,
        status: str,
        location: Optional[str] = None,
        retry_after: Optional[int] = None,
        response: Optional[T] = None,
    ):
        self.status = status
        self.location = location
        self.retry_after = retry_after
        self.response = response


class ResourceBase:
    def __repr__(self):
        return main_object_repr(self)
