from io import BytesIO
from unittest.mock import MagicMock

import boto3
import pytest
from PIL import Image
from botocore.exceptions import ClientError

from image_resizer.image import ImageFormat
from image_resizer.storage import StorageOperationError, save, load


@pytest.mark.parametrize(
    "file_format,content_type",
    [(ImageFormat.JPEG, "image/jpeg"), (ImageFormat.PNG, "image/png")],
)
def test_sut_sends_command_to_client_correctly(file_format, content_type):
    # Arrange
    sut = save
    bucket = "bucket"
    path = "path/to/file"
    stream = BytesIO()
    client_spy = MagicMock()

    # Act
    sut(
        client_spy,
        bucket,
        path,
        stream,
        file_format,
    )

    # Assert
    client_spy.put_object.assert_called_once_with(
        Bucket=bucket, Key=path, Body=b"", ContentType=content_type
    )


def test_sut_raises_storage_operation_error_if_client_error_happens():
    # Arrange
    sut = save
    bucket = "bucket"
    path = "path/to/file"
    stream = BytesIO()
    client_stub = MagicMock()
    client_stub.put_object.side_effect = ClientError({}, "PutObject")

    # Act & Assert
    with pytest.raises(StorageOperationError):
        sut(client_stub, bucket, path, stream, ImageFormat.JPEG)


@pytest.mark.skip(reason="DoC test with real AWS identity and S3")
def test_sut_saves_io_stream_correctly():
    # Arrange
    sut = save
    client = boto3.client("s3", "ap-northeast-2")
    bucket = "com.gnsister"
    path = "arine.png"
    image = Image.open("tests/sample_image.jpg")
    fmt = ImageFormat.JPEG
    stream = BytesIO()
    image.save(stream, format=fmt.name, optimize=True, quality=80)

    # Act
    sut(client, bucket, path, stream, fmt)

    # Assert
    stream, fmt = load(client, bucket, path)
    _ = Image.open(stream, formats=[fmt.name])


def _client_normal_response(status_code: int) -> dict:
    return {
        "ResponseMetadata": {
            "HTTPStatusCode": status_code,
        }
    }
