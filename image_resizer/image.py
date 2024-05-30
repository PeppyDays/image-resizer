from __future__ import annotations

from enum import Enum
from io import BytesIO

from PIL import Image

DEFAULT_QUALITY = 80
MAX_WIDTH_FOR_RESIZING_EXACTLY = 2000
MAX_HEIGHT_FOR_RESIZING_EXACTLY = 5000


def resize(
    stream: BytesIO,
    fmt: ImageFormat,
    width: int | None,
    height: int | None,
    quality: int | None,
) -> BytesIO:
    _check_negative_length(width, height)
    _check_too_long_length(width, height)

    # Set default quality as 80
    quality = DEFAULT_QUALITY if quality is None else quality

    # If both width and height are None, return the original image
    if width is None and height is None:
        return stream

    # If one of width and height is None, resize the image keeping the ratio
    if width is not None and height is not None:
        resized_stream = _resize_exactly(stream, fmt, width, height, quality)
        stream.close()
        return resized_stream

    # If both width and height are not None, resize the image exactly and ignore the ratio
    resized_stream = _resize_proportionally(stream, fmt, width, height, quality)
    stream.close()
    return resized_stream


def _check_negative_length(width: int | None, height: int | None):
    if width is not None and width <= 0:
        raise ValueError(f"Width {width} cannot be negative")
    if height is not None and height <= 0:
        raise ValueError(f"Height {height} cannot be negative")


def _check_too_long_length(width, height):
    if (
        width is not None
        and width > MAX_WIDTH_FOR_RESIZING_EXACTLY
        and height is not None
    ):
        raise ValueError(
            f"Width cannot be longer than {MAX_WIDTH_FOR_RESIZING_EXACTLY} px"
        )
    if (
        height is not None
        and height > MAX_HEIGHT_FOR_RESIZING_EXACTLY
        and width is not None
    ):
        raise ValueError(
            f"Width cannot be longer than {MAX_HEIGHT_FOR_RESIZING_EXACTLY} px"
        )


def _resize_exactly(
    stream: BytesIO, fmt: ImageFormat, width: int, height: int, quality: int
) -> BytesIO:
    image = Image.open(stream, formats=[fmt.name()])
    image = image.resize((width, height))
    return _convert_image_to_bytes_stream(image, fmt, quality)


def _resize_proportionally(
    stream: BytesIO,
    fmt: ImageFormat,
    width: int | None,
    height: int | None,
    quality: int,
) -> BytesIO:
    image = Image.open(stream, formats=[fmt.name()])
    width, height = _fill_missing_length(image.width, image.height, width, height)
    image.thumbnail((width, height))
    return _convert_image_to_bytes_stream(image, fmt, quality)


def _fill_missing_length(
    image_width: int,
    image_height: int,
    requested_width: int | None,
    requested_height: int | None,
) -> tuple[int, int]:
    width, height = image_width, image_height
    if requested_width is not None:
        width = requested_width
    if requested_height is not None:
        height = requested_height
    return width, height


def _convert_image_to_bytes_stream(
    image: Image, fmt: ImageFormat, quality: int
) -> BytesIO:
    stream = BytesIO()
    image.save(stream, format=fmt.name(), optimize=True, quality=quality)
    return stream


class ImageFormat(Enum):
    JPEG = "JPEG"
    PNG = "PNG"
    GIF = "GIF"
    WEBP = "WEBP"
    TIFF = "TIFF"

    def __str__(self):
        return self.value

    def name(self):
        return self.value

    @staticmethod
    def convert_from(content_type: str) -> ImageFormat:
        match content_type:
            case "image/jpeg":
                return ImageFormat.JPEG
            case "image/png":
                return ImageFormat.PNG
            case "image/gif":
                return ImageFormat.GIF
            case "image/webp":
                return ImageFormat.WEBP
            case "image/tiff":
                return ImageFormat.TIFF
            case _:
                raise NotImplementedError(f"Unsupported image format: {content_type}")

    def convert_to(self) -> str:
        match self:
            case ImageFormat.JPEG:
                return "image/jpeg"
            case ImageFormat.PNG:
                return "image/png"
            case ImageFormat.GIF:
                return "image/gif"
            case ImageFormat.WEBP:
                return "image/webp"
            case ImageFormat.TIFF:
                return "image/tiff"
