from datetime import datetime, timezone

from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from rhdllib.auth import FlaskHmacSignature, HmacSignature


def create_test_request(method="GET", json=None, headers=None, args=None, path="/"):
    builder = EnvironBuilder(
        method=method, json=json, headers=headers, query_string=args, path=path
    )
    env = builder.get_environ()
    request = Request(env)
    return request


def test_rhdl_hmac_signature_is_valid():
    string_now = "20240919T132539Z"
    test_request = create_test_request(
        method="GET",
        path="/api/v1/jobs",
        headers={
            "User-Agent": "python-requests/2.27.1",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Host": "127.0.0.1:5000",
            "X-RHDL-Date": string_now,
            "Authorization": "RHDL-HMAC-SHA256 Credential=remoteci/5bb5c0ed-78f6-4e99-aa02-918c4677a97f/20240919/BHS3/api/rhdl_request, SignedHeaders=host;x-rhdl-date, Signature=8026d9fa65b349cb77520be3f0d49f558a5b6130ebf2ec7d5acd2932c5173a2e",
        },
    )
    now = datetime.strptime(string_now, "%Y%m%dT%H%M%SZ")
    now = now.replace(tzinfo=timezone.utc)
    options = {
        "service_name": "api",
        "service_key": "rhdl_request",
        "region_name": "BHS3",
        "algorithm": "RHDL-HMAC-SHA256",
    }
    signature = FlaskHmacSignature(options, now).add_request(test_request)
    assert signature.access_key == "remoteci/5bb5c0ed-78f6-4e99-aa02-918c4677a97f"
    assert signature.is_valid(
        secret_key="9i9U20riVIBhTeCcXzhyqcVJHHIbWY4veo2Bfdn14NgvCaKw2JJYTm0tIHpGyk8w"
    )


def test_rhdl_hmac_signature_is_expired():
    twenty_min_before_now = "20240919T132539Z"
    test_request = create_test_request(
        method="GET",
        path="/api/v1/jobs",
        headers={
            "User-Agent": "python-requests/2.27.1",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Host": "127.0.0.1:5000",
            "X-RHDL-Date": twenty_min_before_now,
            "Authorization": "RHDL-HMAC-SHA256 Credential=remoteci/5bb5c0ed-78f6-4e99-aa02-918c4677a97f/20240919/BHS3/api/rhdl_request, SignedHeaders=host;x-rhdl-date, Signature=8026d9fa65b349cb77520be3f0d49f558a5b6130ebf2ec7d5acd2932c5173a2e",
        },
    )
    now = datetime.strptime("20240919T134539Z", "%Y%m%dT%H%M%SZ")
    now = now.replace(tzinfo=timezone.utc)
    options = {
        "service_name": "api",
        "service_key": "rhdl_request",
        "region_name": "BHS3",
        "algorithm": "RHDL-HMAC-SHA256",
    }
    signature = FlaskHmacSignature(options, now).add_request(test_request)
    assert (
        signature.is_valid(
            "9i9U20riVIBhTeCcXzhyqcVJHHIbWY4veo2Bfdn14NgvCaKw2JJYTm0tIHpGyk8w"
        )
        is False
    )
    assert signature.error_message == "signature is expired"


def test_signature_invalid_if_request_tempered():
    string_now = "20240919T132539Z"
    test_request = create_test_request(
        method="GET",
        path="/api/v1/admin",
        headers={
            "User-Agent": "python-requests/2.27.1",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Host": "127.0.0.1:5000",
            "X-RHDL-Date": string_now,
            "Authorization": "RHDL-HMAC-SHA256 Credential=remoteci/5bb5c0ed-78f6-4e99-aa02-918c4677a97f/20240919/BHS3/api/rhdl_request, SignedHeaders=host;x-rhdl-date, Signature=8026d9fa65b349cb77520be3f0d49f558a5b6130ebf2ec7d5acd2932c5173a2e",
        },
    )
    now = datetime.strptime(string_now, "%Y%m%dT%H%M%SZ")
    now = now.replace(tzinfo=timezone.utc)
    options = {
        "service_name": "api",
        "service_key": "rhdl_request",
        "region_name": "BHS3",
        "algorithm": "RHDL-HMAC-SHA256",
    }
    signature = FlaskHmacSignature(options, now).add_request(test_request)
    assert (
        signature.is_valid(
            "9i9U20riVIBhTeCcXzhyqcVJHHIbWY4veo2Bfdn14NgvCaKw2JJYTm0tIHpGyk8w"
        )
        is False
    )
    assert signature.error_message == "signature invalid"


def test_generate_headers():
    string_now = "20240919T132539Z"
    now = datetime.strptime(string_now, "%Y%m%dT%H%M%SZ")
    now = now.replace(tzinfo=timezone.utc)
    options = {
        "service_name": "api",
        "service_key": "rhdl_request",
        "region_name": "BHS3",
        "algorithm": "RHDL-HMAC-SHA256",
    }
    request = {
        "method": "GET",
        "params": {},
        "json": {},
        "host": "127.0.0.1:5000",
        "path": "/api/v1/jobs",
    }
    signature = HmacSignature(options, now).add_request(request)
    credentials = {
        "access_key": "remoteci/5bb5c0ed-78f6-4e99-aa02-918c4677a97f",
        "secret_key": "9i9U20riVIBhTeCcXzhyqcVJHHIbWY4veo2Bfdn14NgvCaKw2JJYTm0tIHpGyk8w",
    }
    assert signature.generate_headers(credentials) == {
        "host": "127.0.0.1:5000",
        "x-rhdl-date": string_now,
        "authorization": "RHDL-HMAC-SHA256 Credential=remoteci/5bb5c0ed-78f6-4e99-aa02-918c4677a97f/20240919/BHS3/api/rhdl_request, SignedHeaders=host;x-rhdl-date, Signature=8026d9fa65b349cb77520be3f0d49f558a5b6130ebf2ec7d5acd2932c5173a2e",
    }
