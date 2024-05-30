from io import BytesIO

from botocore.exceptions import ClientError

from .image import ImageFormat


def load(client, bucket: str, path: str) -> tuple[BytesIO, ImageFormat]:
    try:
        response = client.get_object(Bucket=bucket, Key=path)
        fmt = ImageFormat.convert_from(response["ContentType"])
        stream = BytesIO(response["Body"].read())
        return stream, fmt
    except ClientError as e:
        if e.response.get("Error", {}).get("Code", None) == "NoSuchKey":
            raise FileNotFoundError(f"File not found in S3: {bucket}/{path}") from e
        raise RuntimeError(f"Failed to load image from S3: {bucket}/{path}") from e
