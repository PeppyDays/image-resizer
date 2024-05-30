import pytest

from image_resizer.request import parse, take_resizing_hint


def test_sut_removes_resizing_hint_from_uri_if_resizing_hint_is_given():
    # Arrange
    sut = take_resizing_hint
    request = _request(
        "/path/to/file_T.png",
        "w=100&h=90&q=70",
        "hello.s3.ap-northeast-2.amazonaws.com",
    )

    # Act
    updated_request = sut(request)

    # Assert
    actual = updated_request["uri"]
    assert actual == "/path/to/file.png"


@pytest.mark.parametrize(
    "resizing_hint,expected", [("_T", 100), ("_S", 200), ("_M", 300), ("_L", 400)]
)
def test_sut_updates_width_in_query_string_if_resizing_hint_is_given(
    resizing_hint, expected
):
    # Arrange
    sut = take_resizing_hint
    request = _request(
        f"/path/to/file{resizing_hint}.png",
        "w=900&h=90&q=70",
        "hello.s3.ap-northeast-2.amazonaws.com",
    )

    # Act
    updated_request = sut(request)

    # Assert
    actual = updated_request["querystring"]
    assert f"w={expected}" in actual


@pytest.mark.parametrize("query_string", ["w=100&h=90&q=70", "h=980", "w=100"])
def test_sut_removes_height_from_query_string_if_resizing_hint_is_given(query_string):
    # Arrange
    sut = take_resizing_hint
    request = _request(
        "/path/to/file_L.png",
        query_string,
        "hello.s3.ap-northeast-2.amazonaws.com",
    )

    # Act
    updated_request = sut(request)

    # Assert
    actual = updated_request["querystring"]
    assert "h=" not in actual


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
