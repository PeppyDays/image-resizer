import re
from urllib.parse import parse_qs, unquote, urlencode

# Map of resizing hint and expected width
RESIZING_HINT = {
    "_t": 100,
    "_s": 200,
    "_m": 300,
    "_l": 400,
}


def take_resizing_hint(request: dict) -> dict:
    resizing_hint, uri = _parse_resizing_hint_and_uri(request)
    if resizing_hint is None:
        return request

    width = RESIZING_HINT[resizing_hint]
    query_params = _parse_query_params(request)
    query_params["w"] = str(width)
    query_params.pop("h", None)
    request["uri"] = uri
    request["querystring"] = urlencode(query_params)
    return request


def parse(request: dict) -> tuple[str, str, int | None, int | None, int | None]:
    path = _parse_path(request)
    bucket = _parse_bucket(request)
    query_params = _parse_query_params(request)
    width = _parse_width(query_params)
    height = _parse_height(query_params)
    quality = _parse_quality(query_params)
    return bucket, path, width, height, quality


def _parse_resizing_hint_and_uri(request: dict) -> tuple[str | None, str]:
    # "/path/to", "hello_t.png" <- "/path/to/hello_t.png"
    directory_path, file_name_with_extension = request["uri"].rsplit("/", 1)
    # "hello_t", "png" <- "hello_t.png"
    file_name, extension = file_name_with_extension.rsplit(".", 1)
    # "hello", "_t" <- "hello_t"
    file_name_without_resizing_hint, resizing_hint = file_name[:-2], file_name[-2:]

    if resizing_hint in RESIZING_HINT:
        uri = f"{directory_path}/{file_name_without_resizing_hint}.{extension}"
        return resizing_hint, uri

    return None, request["uri"]


def _parse_path(request) -> str:
    path = unquote(request.get("uri", "")).lstrip("/")
    return path


def _parse_bucket(request) -> str:
    pattern = re.compile(r"\.s3\.[a-z-1-9]+?\.amazonaws\.com")
    bucket = pattern.sub("", request.get("origin", {}).get("s3", {}).get("domainName"))
    return bucket


def _parse_query_params(request):
    return {k: v[0] for k, v in parse_qs(request.get("querystring", "")).items()}


def _parse_width(query_params) -> int | None:
    width = query_params.get("w")
    if width:
        width = int(width)
    return width


def _parse_height(query_params) -> int | None:
    height = query_params.get("h")
    if height:
        height = int(height)
    return height


def _parse_quality(query_params) -> int | None:
    quality = query_params.get("q")
    if quality:
        quality = int(quality)
    return quality
