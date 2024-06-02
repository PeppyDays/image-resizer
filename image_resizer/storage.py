from io import BytesIO

from botocore.exceptions import ClientError

from .image import ImageFormat


def load(client, bucket: str, path: str) -> tuple[BytesIO, ImageFormat]:
    try:
        response = client.get_object(Bucket=bucket, Key=path)
        fmt = ImageFormat.try_from(response["ContentType"])
        stream = BytesIO(response["Body"].read())
        return stream, fmt
    except ClientError as e:
        if e.response.get("Error", {}).get("Code", None) == "NoSuchKey":
            raise ObjectNotFoundError(f"File not found in S3: {bucket}/{path}") from e
        raise StorageOperationError(
            f"Failed to load image from S3: {bucket}/{path}"
        ) from e


def save(client, bucket: str, path: str, stream: BytesIO, fmt: ImageFormat) -> None:
    try:
        client.put_object(
            Bucket=bucket,
            Key=path,
            Body=stream.getvalue(),
            ContentType=fmt.value,
        )
    except ClientError as e:
        raise StorageOperationError(
            f"Failed to save image to S3: {bucket}/{path}"
        ) from e


class ObjectNotFoundError(FileNotFoundError):
    def __init__(self, message: str):
        super().__init__(message)


class StorageOperationError(RuntimeError):
    def __init__(self, message: str):
        super().__init__(message)
