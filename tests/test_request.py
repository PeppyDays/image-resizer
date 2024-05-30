import pytest

from image_resizer.request import parse


@pytest.mark.parametrize(
    "origin,expected",
    [
        ("hello.s3.ap-northeast-2.amazonaws.com", "hello"),
        ("hi-there.s3.ap-northeast-2.amazonaws.com", "hi-there"),
        ("com.hp.s3.ap-northeast-2.amazonaws.com", "com.hp"),
        ("hp.s3.hp.s3.ap-northeast-2.amazonaws.com", "hp.s3.hp"),
    ],
)
def test_sut_parses_bucket_correctly(origin, expected):
    # Arrange
    sut = parse
    request = _request("/path/to/file", "w=100&h=90&q=70", origin)

    # Act
    actual, _, _, _, _ = sut(request)

    # Assert
    assert actual == expected


@pytest.mark.parametrize("uri,expected", [("/path/to/file", "path/to/file")])
def test_sut_parses_path_without_prefix_slash(uri, expected):
    # Arrange
    sut = parse
    request = _request(uri, "w=100&h=90&q=70", "hello.s3.ap-northeast-2.amazonaws.com")

    # Act
    _, actual, _, _, _ = sut(request)

    # Assert
    assert actual == expected


@pytest.mark.parametrize(
    "uri,expected",
    [
        (
            "/path/to/%ED%95%9C%EA%B8%80%ED%8C%8C%EC%9D%BC%EB%AA%85.png",
            "path/to/한글파일명.png",
        )
    ],
)
def test_sut_parses_url_encoded_path(uri, expected):
    # Arrange
    sut = parse
    request = _request(uri, "w=100&h=90&q=70", "hello.s3.ap-northeast-2.amazonaws.com")

    # Act
    _, actual, _, _, _ = sut(request)

    # Assert
    assert actual == expected


def test_sut_parses_width_as_none_if_not_provided():
    # Arrange
    sut = parse
    request = _request(
        "/path/to/file", "h=100&q=70", "hello.s3.ap-northeast-2.amazonaws.com"
    )

    # Act
    _, _, actual, _, _ = sut(request)

    # Assert
    assert actual is None


def test_sut_parses_width_correctly():
    # Arrange
    sut = parse
    request = _request(
        "/path/to/file", "w=100&h=90&q=70", "hello.s3.ap-northeast-2.amazonaws.com"
    )

    # Act
    _, _, actual, _, _ = sut(request)

    # Assert
    assert actual == 100


def test_sut_parses_height_as_none_if_not_provided():
    # Arrange
    sut = parse
    request = _request(
        "/path/to/file", "w=100&q=80", "hello.s3.ap-northeast-2.amazonaws.com"
    )

    # Act
    _, _, _, actual, _ = sut(request)

    # Assert
    assert actual is None


def test_sut_parses_height_correctly():
    # Arrange
    sut = parse
    request = _request(
        "/path/to/file", "w=100&h=90&q=70", "hello.s3.ap-northeast-2.amazonaws.com"
    )

    # Act
    _, _, _, actual, _ = sut(request)

    # Assert
    assert actual == 90


def test_sut_parses_quality_as_none_if_not_provided():
    # Arrange
    sut = parse
    request = _request(
        "/path/to/file", "w=100&h=90", "hello.s3.ap-northeast-2.amazonaws.com"
    )

    # Act
    _, _, _, _, actual = sut(request)

    # Assert
    assert actual is None


def test_sut_parses_quality_correctly():
    # Arrange
    sut = parse
    request = _request(
        "/path/to/file", "w=100&h=90&q=70", "hello.s3.ap-northeast-2.amazonaws.com"
    )

    # Act
    _, _, _, _, actual = sut(request)

    # Assert
    assert actual == 70


def _request(uri: str, query_string: str, origin: str) -> dict:
    assert uri.startswith("/")
    return {
        "uri": uri,
        "querystring": query_string,
        "origin": {"s3": {"domainName": origin}},
    }
