import re
from urllib import parse as qs_parse


def parse(request: dict) -> tuple[str, str, int | None, int | None, int | None]:
    path = _parse_path(request)
    bucket = _parse_bucket(request)
    query_params = {
        k: v[0] for k, v in qs_parse.parse_qs(request.get("querystring", "")).items()
    }
    width = _parse_width(query_params)
    height = _parse_height(query_params)
    quality = _parse_quality(query_params)
    return bucket, path, width, height, quality


def _parse_path(request) -> str:
    path = qs_parse.unquote(request.get("uri", "")).lstrip("/")
    return path


def _parse_bucket(request) -> str:
    pattern = re.compile(r"\.s3\.[a-z-1-9]+?\.amazonaws\.com")
    bucket = pattern.sub("", request.get("origin", {}).get("s3", {}).get("domainName"))
    return bucket


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
