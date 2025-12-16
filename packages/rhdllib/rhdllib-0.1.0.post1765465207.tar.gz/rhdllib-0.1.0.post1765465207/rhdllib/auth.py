#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta, timezone

from requests.auth import AuthBase
from urllib.parse import unquote
from urllib.parse import quote
from urllib.parse import parse_qsl
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


TIMESTAMP_FORMAT = "%Y%m%dT%H%M%SZ"


class BaseHmacSignature:
    def __init__(self, options, now=None):
        self.now = datetime.now(timezone.utc) if now is None else now
        self.error_message = ""
        self.algorithm = options["algorithm"]
        self.service_name = options["service_name"]
        self.service_key = options["service_key"]
        self.region_name = options["region_name"]
        self.date_header = (
            "x-amz-date" if self.service_key == "aws4_request" else "x-rhdl-date"
        )

    def add_request(self, request):
        logger.debug("Calculating signature using v4 auth.")
        self.parse_request(request)
        self.canonical_request = self._get_canonical_request()
        logger.debug(f"Canonical request:\n{self.canonical_request}")
        self.string_to_sign = self._get_string_to_sign()
        logger.debug(f"String to sign:\n{self.string_to_sign}")
        return self

    def parse_request(self, request):
        raise NotImplementedError

    def _get_canonical_querystring(self, args):
        key_val_pairs = []
        for key, value in args.items():
            key_val_pairs.append(
                (quote(key, safe="_.-~"), quote(str(value), safe="_.-~"))
            )

        sorted_key_vals_pairs = []
        for key, value in sorted(key_val_pairs):
            sorted_key_vals_pairs.append(f"{key}={value}")
        canonical_query_string = "&".join(sorted_key_vals_pairs)
        return canonical_query_string

    def _get_canonical_headers(self, headers_to_sign):
        headers = []
        for key in sorted(headers_to_sign):
            value = " ".join(headers_to_sign[key].split())
            headers.append(f"{key}:{value}")
        return "\n".join(headers)

    def _get_signed_headers(self, headers_to_sign):
        headers = sorted(headers_to_sign)
        return ";".join(headers)

    def _encode_data(self, data):
        try:
            return (data or "").encode("utf-8")
        except (UnicodeDecodeError, AttributeError):
            return data

    def _get_payload(self, data):
        data = self._encode_data(data)
        if data and hasattr(data, "seek"):
            position = data.tell()
            performant_payload_buffer = 1024 * 1024
            read_chunksize = functools.partial(data.read, performant_payload_buffer)
            checksum = hashlib.sha256()
            for chunk in iter(read_chunksize, b""):
                checksum.update(chunk)
            hex_checksum = checksum.hexdigest()
            data.seek(position)
            return hex_checksum
        return hashlib.sha256(data).hexdigest()

    def _get_canonical_request(self):
        canonical_request = [
            self.method,
            unquote(self.path),
            self._get_canonical_querystring(self.params),
            self._get_canonical_headers(self.headers_to_sign) + "\n",
            self._get_signed_headers(self.headers_to_sign),
            self._get_payload(self.data),
        ]
        return "\n".join(canonical_request)

    def _get_credential_scope(self):
        credential_scope = [
            self.timestamp[0:8],
            self.region_name,
            self.service_name,
            self.service_key,
        ]
        return "/".join(credential_scope)

    def _hash_sha256(self, msg):
        return hashlib.sha256(msg.encode("utf-8")).hexdigest()

    def _get_string_to_sign(self):
        string_to_sign = [
            self.algorithm,
            self.timestamp,
            self._get_credential_scope(),
            self._hash_sha256(self.canonical_request),
        ]
        return "\n".join(string_to_sign)

    def _sign_hex(self, key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).hexdigest()

    def _sign(self, key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def _get_signature(self, secret_key):
        algo_version = self.algorithm.replace("-HMAC-SHA256", "")
        k_date = self._sign(
            (f"{algo_version}{secret_key}").encode("utf-8"), self.timestamp[0:8]
        )
        k_region = self._sign(k_date, self.region_name)
        k_service = self._sign(k_region, self.service_name)
        k_signing = self._sign(k_service, self.service_key)
        return self._sign_hex(k_signing, self.string_to_sign)

    def _signature_equals(self, signature1, signature2):
        return hmac.compare_digest(
            signature1.encode("utf-8"), signature2.encode("utf-8")
        )


class FlaskHmacSignature(BaseHmacSignature):
    def parse_request(self, request):
        self.parse_headers(request.headers)
        self.method = request.method.upper()
        self.path = request.path
        self.params = request.args
        self.data = request.data

    def parse_headers(self, headers):
        logger.debug(f"Request headers:\n{headers}")
        lower_headers = {key.lower(): value for key, value in headers.items()}
        for key, value in lower_headers.items():
            value = value.strip()
            if key == self.date_header:
                self.timestamp = value
            if key == "authorization":
                _, credential, signed_headers, signature = value.split(" ")
                credential = (
                    credential.replace("Credential=", "").replace(",", "").split("/")
                )
                if len(credential) < 5:
                    raise Exception("Credential invalid")
                self.access_key = "/".join(credential[:-4])
                signed_headers = [
                    h.lower().strip()
                    for h in signed_headers.replace("SignedHeaders=", "")
                    .replace(",", "")
                    .split(";")
                ]
                self.headers_to_sign = {
                    h: lower_headers[h] for h in set(signed_headers)
                }
                self.signature_in_header = signature.replace("Signature=", "")

    def is_expired(self):
        if self.timestamp:
            timestamp = datetime.strptime(self.timestamp, TIMESTAMP_FORMAT)
            timestamp = timestamp.replace(tzinfo=timezone.utc)
            fifteen_min = timedelta(minutes=15)
            return abs(self.now - timestamp) > fifteen_min
        return True

    def is_valid(self, secret_key):
        if self.is_expired():
            self.error_message = "signature is expired"
            return False
        signatures_equals = self._signature_equals(
            self._get_signature(secret_key), self.signature_in_header
        )
        if not signatures_equals:
            self.error_message = "signature invalid"
        return signatures_equals


class HmacSignature(BaseHmacSignature):
    def parse_request(self, request):
        self.timestamp = datetime.strftime(self.now, TIMESTAMP_FORMAT)
        self.headers_to_sign = {
            "host": request["host"],
            self.date_header: self.timestamp,
        }
        self.method = request["method"]
        self.path = request["path"]
        self.params = request["params"]
        if "json" in request and request["json"]:
            self.data = json.dumps(request["json"])
        else:
            self.data = request.get("data", "")
        self.host = request["host"]

    def generate_headers(self, credentials):
        self.access_key = credentials["access_key"]
        signature = self._get_signature(credentials["secret_key"])

        authorization_header = [
            f"{self.algorithm} Credential={self.access_key}/{self._get_credential_scope()}"
        ]
        authorization_header.append(
            f"SignedHeaders={self._get_signed_headers(self.headers_to_sign)}"
        )
        authorization_header.append("Signature=%s" % signature)
        return {
            "host": self.host,
            self.date_header: self.timestamp,
            "authorization": ", ".join(authorization_header),
        }


class HmacAuthBase(AuthBase):
    """Extend AuthBase from python requests with HMAC authentication"""

    def __init__(
        self,
        access_key,
        secret_key,
        service,
        region,
        service_key="rhdl_request",
        algorithm="RHDL-HMAC-SHA256",
    ):
        self.access_key = access_key
        self.secret_key = secret_key
        self.service = service
        self.region = region
        self.service_key = service_key
        self.algorithm = algorithm

    def __call__(self, r):
        url = urlparse(r.url)
        signature = HmacSignature(
            {
                "service_name": self.service,
                "service_key": self.service_key,
                "region_name": self.region,
                "algorithm": self.algorithm,
            }
        ).add_request(
            {
                "method": r.method,
                "params": dict(parse_qsl(url.query)),
                "data": self.get_body(r.body),
                "host": url.netloc,
                "path": url.path,
            }
        )
        r.headers.update(
            signature.generate_headers(
                {
                    "access_key": self.access_key,
                    "secret_key": self.secret_key,
                },
            )
        )
        return r

    def get_body(self, body):
        if hasattr(body, "read"):
            c = body.read()
            body.seek(0)
            return c
        return body
