from io import BytesIO
from unittest.mock import MagicMock

import boto3
import pytest
from PIL import Image
from botocore.exceptions import ClientError
from botocore.response import StreamingBody

from image_resizer.image import ImageFormat, UnsupportedImageFormatError
from image_resizer.storage import load, ObjectNotFoundError, StorageOperationError


def test_sut_send_command_to_client_correctly():
    # Arrange
    sut = load
    bucket = "bucket"
    path = "path/to/file"
    client_spy = MagicMock()
    client_spy.get_object.return_value = _client_normal_response("image/png", b"")

    # Act
    sut(client_spy, bucket, path)

    # Assert
    client_spy.get_object.assert_called_once_with(Bucket=bucket, Key=path)


def test_sut_raises_object_not_found_error_if_the_requested_path_does_not_exist():
    # Arrange
    sut = load
    bucket = "bucket"
    path = "path/to/file"
    client_stub = MagicMock()
    client_stub.get_object.side_effect = _client_no_suck_key_error_response(path)

    # Act & Assert
    with pytest.raises(ObjectNotFoundError):
        sut(client_stub, bucket, path)


def test_sut_raises_storage_operation_error_if_client_error_happens():
    # Arrange
    sut = load
    bucket = "bucket"
    path = "path/to/file"
    client_stub = MagicMock()
    client_stub.get_object.side_effect = ClientError({}, "GetObject")

    # Act & Assert
    with pytest.raises(StorageOperationError):
        sut(client_stub, bucket, path)


@pytest.mark.parametrize(
    "content_type,expected",
    [
        ("image/jpeg", ImageFormat.JPEG),
        ("image/png", ImageFormat.PNG),
        ("image/gif", ImageFormat.GIF),
        ("image/webp", ImageFormat.WEBP),
        ("image/tiff", ImageFormat.TIFF),
    ],
)
def test_sut_returns_image_format_correctly(content_type, expected):
    # Arrange
    sut = load
    bucket = "bucket"
    path = "path/to/file"
    client_stub = MagicMock()
    client_stub.get_object.return_value = _client_normal_response(content_type, b"")

    # Act
    stream, actual = sut(client_stub, bucket, path)

    # Assert
    assert actual == expected


def test_sut_raises_unsupported_image_format_error_if_image_format_is_unsupported():
    # Arrange
    sut = load
    bucket = "bucket"
    path = "path/to/file"
    client_stub = MagicMock()
    client_stub.get_object.return_value = _client_normal_response(
        "image/unsupported", b""
    )

    # Act & Assert
    with pytest.raises(UnsupportedImageFormatError):
        sut(client_stub, bucket, path)


@pytest.mark.skip(reason="DoC test with real AWS identity and S3")
def test_sut_returns_io_stream_correctly():
    # Arrange
    sut = load
    client = boto3.client("s3", "ap-northeast-2")
    bucket = "com.gnsister"
    path = "brown.png"

    # Act
    stream, fmt = sut(client, bucket, path)

    # Assert
    Image.open(
        stream,
        formats=[fmt.name],
    ).save("resized.png", format=fmt.name)


def _client_no_suck_key_error_response(path) -> ClientError:
    client_response = {
        "Error": {
            "Code": "NoSuchKey",
            "Message": "The specified key does not exist",
            "Key": path,
        }
    }
    client_operation_name = "GetObject"
    return ClientError(client_response, client_operation_name)


def _client_normal_response(content_type: str, raw_stream: bytes) -> dict:
    return {
        "ContentType": content_type,
        "Body": StreamingBody(BytesIO(raw_stream), len(raw_stream)),
    }
