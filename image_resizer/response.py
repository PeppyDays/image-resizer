import base64
from http import HTTPStatus
from io import BytesIO

from .image import ImageFormat, InvalidImageRequestError, UnsupportedImageFormatError
from .storage import ObjectNotFoundError


def finalize(
    response: dict,
    stream: BytesIO,
    fmt: ImageFormat | None,
    exception: Exception | None = None,
) -> dict:
    # If no errors occurred, update the response as successful
    if exception is None:
        _check_mandatory_parameters(stream, fmt)
        _update_status_as(response, HTTPStatus.OK)
        _update_body_as(response, stream, fmt)
        _update_cache_control_as(response, 31536000)
    # Add special handling for specific exceptions
    elif isinstance(exception, InvalidImageRequestError):
        _update_status_as(response, HTTPStatus.BAD_REQUEST)
    elif isinstance(exception, ObjectNotFoundError):
        _update_status_as(response, HTTPStatus.NOT_FOUND)
    # Add pass through for listed exceptions
    elif isinstance(exception, UnsupportedImageFormatError):
        pass
    # Other unexpected errors are handled as internal server errors
    elif isinstance(exception, Exception):
        _update_status_as(response, HTTPStatus.INTERNAL_SERVER_ERROR)

    if not stream.closed:
        stream.close()

    return response


def _check_mandatory_parameters(
    stream: BytesIO | None, fmt: ImageFormat | None
) -> None:
    if stream is None or fmt is None:
        raise ValueError("Mandatory parameters are missing")


def _update_body_as(
    response: dict,
    stream: BytesIO,
    fmt: ImageFormat,
) -> None:
    response["bodyEncoding"] = "base64"
    response["body"] = base64.standard_b64encode(stream.getvalue()).decode()
    response["headers"]["content-type"] = [
        {"key": "Content-Type", "value": fmt.value},
    ]


def _update_status_as(response: dict, status: HTTPStatus) -> None:
    response["status"] = status.value
    response["statusDescription"] = status.phrase


def _update_cache_control_as(response: dict, max_age: int) -> None:
    response["headers"]["cache-control"] = [
        {"key": "Cache-Control", "value": f"max-age={max_age}"},
    ]
