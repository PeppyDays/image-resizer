import copy

import pytest

from image_resizer.request import take_resizing_hint


@pytest.mark.parametrize(
    "uri,expected",
    [
        ("/path/to/file_t.png", "/path/to/file.png"),
        ("/path/to/file_s.png", "/path/to/file.png"),
        ("/path/to/file_m.png", "/path/to/file.png"),
        ("/path/to/file_l.png", "/path/to/file.png"),
    ],
)
def test_sut_removes_resizing_hint_from_uri_if_resizing_hint_is_given(uri, expected):
    # Arrange
    sut = take_resizing_hint
    request = _request(
        uri,
        "w=100&h=90&q=70",
        "hello.s3.ap-northeast-2.amazonaws.com",
    )

    # Act
    updated_request = sut(request)

    # Assert
    actual = updated_request["uri"]
    assert actual == expected


@pytest.mark.parametrize(
    "resizing_hint,expected", [("_t", 100), ("_s", 200), ("_m", 300), ("_l", 400)]
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
        "/path/to/file_l.png",
        query_string,
        "hello.s3.ap-northeast-2.amazonaws.com",
    )

    # Act
    updated_request = sut(request)

    # Assert
    actual = updated_request["querystring"]
    assert "h=" not in actual


def test_sut_does_not_change_anything_if_resizing_hint_is_not_found():
    # Arrange
    sut = take_resizing_hint
    request = _request(
        "/path/to/file.png",
        "w=100&h=90&q=70",
        "hello.s3.ap-northeast-2.amazonaws.com",
    )
    expected = copy.deepcopy(request)

    # Act
    actual = sut(request)

    # Assert
    assert actual == expected


def _request(uri: str, query_string: str, origin: str) -> dict:
    assert uri.startswith("/")
    return {
        "uri": uri,
        "querystring": query_string,
        "origin": {"s3": {"domainName": origin}},
    }
