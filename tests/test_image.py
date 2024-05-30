from io import BytesIO

import pytest
from PIL import Image

from image_resizer.image import ImageFormat, resize, InvalidImageRequestError, stamp


@pytest.mark.parametrize("width,height", [(-300, 100), (100, -300)])
def test_sut_raises_image_validation_error_when_requested_length_is_negative(
    original_stream,
    original_format,
    width,
    height,
):
    # Arrange
    sut = resize

    # Act & Assert
    with pytest.raises(InvalidImageRequestError):
        sut(original_stream, original_format, width, height, None)


@pytest.mark.parametrize("width,height", [(2001, 100)])
def test_sut_raises_image_validation_error_when_requested_width_is_longer_than_2000_with_any_height(
    original_stream,
    original_format,
    width,
    height,
):
    # Arrange
    sut = resize

    # Act & Assert
    with pytest.raises(InvalidImageRequestError):
        sut(original_stream, original_format, width, height, None)


@pytest.mark.parametrize("width,height", [(100, 5001)])
def test_sut_raises_image_validation_error_when_requested_height_is_longer_than_5000_with_any_width(
    original_stream,
    original_format,
    width,
    height,
):
    # Arrange
    sut = resize

    # Act & Assert
    with pytest.raises(InvalidImageRequestError):
        sut(original_stream, original_format, width, height, None)


def test_sut_returns_original_image_without_resizing_if_requested_width_and_height_are_none(
    original_stream,
    original_format,
):
    # Arrange
    sut = resize

    # Act
    resized_stream = sut(original_stream, original_format, None, None, None)

    # Assert
    assert original_stream == resized_stream


@pytest.mark.parametrize("width,height", [(None, 100), (100, None)])
def test_sut_resizes_image_by_keeping_ratio_if_one_of_width_and_height_is_none(
    original_stream,
    original_format,
    width,
    height,
):
    # Arrange
    sut = resize
    original_image = Image.open(original_stream, formats=[original_format.name()])
    expected = float(original_image.width) / original_image.height

    # Act
    resized_stream = sut(original_stream, original_format, width, height, None)

    # Assert
    resized_image = Image.open(resized_stream, formats=[original_format.name()])
    actual = float(resized_image.width) / resized_image.height
    assert actual == pytest.approx(expected, 0.01)


@pytest.mark.parametrize("width,height", [(None, 100), (100, None)])
def test_sut_resizes_image_having_same_length_as_requested_if_one_of_width_and_height_is_none(
    original_stream,
    original_format,
    width,
    height,
):
    # Arrange
    sut = resize

    # Act
    resized_stream = sut(original_stream, original_format, width, height, None)

    # Assert
    actual = Image.open(resized_stream, formats=[original_format.name()])
    assert actual.width == width or actual.height == height


@pytest.mark.parametrize("width,height", [(10000, None), (None, 10000)])
def test_sut_does_not_resize_to_make_bigger_than_original_image_if_one_of_width_and_height_is_none(
    original_stream,
    original_format,
    width,
    height,
):
    # Arrange
    sut = resize
    expected = Image.open(original_stream, formats=[original_format.name()])

    # Act
    resized_stream = sut(original_stream, original_format, width, height, None)

    # Assert
    actual = Image.open(resized_stream, formats=[original_format.name()])
    assert actual.width == expected.width
    assert actual.height == expected.height


@pytest.mark.parametrize("width,height", [(100, 100), (200, 200)])
def test_sut_resizes_exactly_having_same_length_as_requested_if_width_and_heights_are_given(
    original_stream,
    original_format,
    width,
    height,
):
    # Arrange
    sut = resize

    # Act
    resized_stream = sut(original_stream, original_format, width, height, None)

    # Assert
    actual = Image.open(resized_stream, formats=[original_format.name()])
    assert actual.width == width and actual.height == height


@pytest.mark.parametrize("width,height", [(100, 100), (None, 100), (100, None)])
def test_sut_closes_stream_after_actual_resizing(
    original_stream,
    original_format,
    width,
    height,
):
    # Arrange
    sut = resize

    # Act
    sut(original_stream, original_format, 100, 100, None)

    # Assert
    assert original_stream.closed


def test_sut_does_not_close_stream_if_both_width_and_height_are_none(
    original_stream,
    original_format,
):
    # Arrange
    sut = resize

    # Act
    sut(original_stream, original_format, None, None, None)

    # Assert
    assert not original_stream.closed


def test_sut_overlaps_watermark_on_image_correctly(original_stream, original_format):
    # Arrange
    sut = stamp

    # Act
    watermarked_stream = sut(
        original_stream,
        original_format,
    )

    # Assert
    watermarked_image = Image.open(watermarked_stream)
    watermarked_image.save(
        "images/output.jpg",
        format=original_format.name(),
    )


@pytest.fixture
def original_stream() -> BytesIO:
    path = "tests/sample_image.jpg"
    return BytesIO(open(path, "rb").read())


@pytest.fixture
def original_format() -> ImageFormat:
    return ImageFormat.JPEG
