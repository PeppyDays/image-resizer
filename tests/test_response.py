import copy
from io import BytesIO

import pytest

from image_resizer.image import ImageFormat
from image_resizer.response import finalize


def test_sut_updates_simple_properties_if_successful_correctly(response):
    # Arrange
    sut = finalize

    # Act
    actual = sut(response, BytesIO(), ImageFormat.JPEG)

    # Assert
    assert actual["status"] == 200


def test_sut_updates_image_related_properties_if_successful_correctly(response):
    # Arrange
    sut = finalize
    stream = BytesIO(open("tests/sample_image.jpg", "rb").read())
    fmt = ImageFormat.JPEG

    # Act
    actual = sut(response, stream, fmt)

    # Assert
    # Skip checking actual body because it is too long
    # assert actual["body"] == "??.."
    assert actual["bodyEncoding"] == "base64"
    assert actual["headers"]["content-type"] == [
        {"key": "Content-Type", "value": "image/jpeg"},
    ]


def test_sut_updates_cache_control_header_if_successful(response):
    # Arrange
    sut = finalize

    # Act
    actual = sut(response, BytesIO(), ImageFormat.PNG)

    # Assert
    assert actual["headers"]["cache-control"] == [
        {"key": "Cache-Control", "value": "max-age=31536000"},
    ]


def test_sut_closes_stream_if_successful(response):
    # Arrange
    sut = finalize
    stream = BytesIO()

    # Act
    sut(response, stream, ImageFormat.PNG)

    # Assert
    assert stream.closed


def test_sut_updates_response_if_value_error_occurred_correctly(response):
    # Arrange
    sut = finalize
    stream = BytesIO()

    # Act
    actual = sut(response, stream, ImageFormat.TIFF, ValueError())

    # Assert
    assert actual["status"] == 400


def test_sut_updates_response_if_file_not_found_correctly(response):
    # Arrange
    sut = finalize
    stream = BytesIO()

    # Act
    actual = sut(
        response,
        stream,
        ImageFormat.JPEG,
        FileNotFoundError(),
    )

    # Assert
    assert actual["status"] == 404


def test_sut_closes_stream_if_file_not_found(response):
    # Arrange
    sut = finalize
    stream = BytesIO()

    # Act
    sut(response, stream, ImageFormat.PNG, FileNotFoundError())

    # Assert
    assert stream.closed


def test_sut_updates_response_if_unexpected_error_occurred_correctly(response):
    # Arrange
    sut = finalize

    # Act
    actual = sut(response, BytesIO(), ImageFormat.JPEG, KeyError())

    # Assert
    assert actual["status"] == 500


def test_sut_closes_stream_if_unexpected_error_occurred(response):
    # Arrange
    sut = finalize
    stream = BytesIO()

    # Act
    sut(response, stream, ImageFormat.PNG, KeyError())

    # Assert
    assert stream.closed


def test_sut_returns_original_response_if_listed_pass_through_errors_occurred(response):
    # Arrange
    sut = finalize
    expected = copy.deepcopy(response)

    # Act
    actual = sut(response, BytesIO(), ImageFormat.JPEG, NotImplementedError())

    # Assert
    assert actual == expected


@pytest.fixture
def response() -> dict:
    return {
        "status": None,
        "statusDescription": None,
        "body": None,
        "bodyEncoding": None,
        "headers": {
            "content-type": {},
            "cache-control": {},
        },
    }
