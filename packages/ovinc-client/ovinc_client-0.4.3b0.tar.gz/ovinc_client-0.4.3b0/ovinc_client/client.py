import hashlib
import os
import time
import uuid
from json import JSONDecodeError

import httpx
from httpx import HTTPStatusError, Response

from ovinc_client.components.auth import Auth
from ovinc_client.components.notice import Notice
from ovinc_client.constants import (
    APP_AUTH_HEADER_APPID_KEY,
    APP_AUTH_HEADER_APPID_NONCE,
    APP_AUTH_HEADER_APPID_SIGN,
    APP_AUTH_HEADER_APPID_TIMESTAMP,
    OVINC_CLIENT_SIGNATURE,
    OVINC_CLIENT_TIMEOUT,
    RequestMethodEnum,
    ResponseData,
)
from ovinc_client.core.logger import logger
from ovinc_client.core.utils import strtobool


class OVINCClient:
    """
    OVINC Union Api Client
    """

    def __init__(self, app_code: str, app_secret: str, union_api_url: str):
        self._app_code = app_code
        self._app_secret = app_secret
        self._union_api_url = union_api_url
        self.notice = Notice(self, self._union_api_url)
        self.auth = Auth(self, self._union_api_url)

    def call_api(self, method: str, url: str, params: dict, timeout: float = OVINC_CLIENT_TIMEOUT) -> ResponseData:
        """
        call union api
        """

        # request
        with httpx.Client(
            http2=True,
            headers=self._build_headers(),
            verify=bool(strtobool(os.getenv("OVINC_API_VERIFY", "True"))),
        ) as client:
            if method == RequestMethodEnum.GET:
                response = client.request(method=method, url=url, timeout=timeout, params=params)
            else:
                response = client.request(method=method, url=url, timeout=timeout, json=params)

        # parse response
        return self._parse_response(response)

    def _build_headers(self) -> dict:
        """
        build request header
        """

        timestamp = str(int(time.time()))
        nonce = uuid.uuid1().hex
        raw_content = f"{timestamp}-{nonce}-{self._app_secret}"
        signature = hashlib.sha256(raw_content.encode()).hexdigest()
        return {
            "User-Agent": OVINC_CLIENT_SIGNATURE,
            APP_AUTH_HEADER_APPID_KEY: self._app_code,
            APP_AUTH_HEADER_APPID_TIMESTAMP: timestamp,
            APP_AUTH_HEADER_APPID_NONCE: nonce,
            APP_AUTH_HEADER_APPID_SIGN: signature,
        }

    @classmethod
    def _parse_response(cls, response: Response) -> ResponseData:
        """
        parse response to json
        """

        try:
            response.raise_for_status()
        except HTTPStatusError as err:
            logger.error("[ResponseCheckFailed] %s", err)
            return ResponseData(result=False)

        try:
            data = response.json()
        except (TypeError, ValueError, JSONDecodeError) as err:
            logger.error("[ResponseParseFailed] %s", err)
            return ResponseData(result=False)

        return ResponseData(result=True, data=data)
