import datetime
import json

from django.conf import settings
from tencentcloud.captcha.v20190722 import captcha_client, models
from tencentcloud.common import credential
from tencentcloud.common.exception import TencentCloudSDKException

from ovinc_client.core.logger import logger
from ovinc_client.tcaptcha.constants import (
    CAPTCHA_TICKET_RET,
    DEFAULT_CAPTCHA_TYPE,
    CaptchaResultCode,
    EvilLevel,
)


class TCaptchaVerify:
    """
    Verify TCaptcha
    """

    def __init__(self, user_ip: str, **kwargs):
        self._cred = credential.Credential(settings.CAPTCHA_TCLOUD_ID, settings.CAPTCHA_TCLOUD_KEY)
        self._client = captcha_client.CaptchaClient(self._cred, "")
        self.user_ip = user_ip
        self.kwargs = kwargs

    def verify(self) -> bool:
        # not enabled
        if not settings.CAPTCHA_ENABLED:
            return True

        # not set or failed
        if not self.kwargs or self.kwargs.get("ret") != CAPTCHA_TICKET_RET:
            return False

        # build params
        params = {
            "CaptchaType": DEFAULT_CAPTCHA_TYPE,
            "Ticket": self.kwargs.get("ticket"),
            "UserIp": self.user_ip,
            "Randstr": self.kwargs.get("randstr"),
            "CaptchaAppId": settings.CAPTCHA_APP_ID,
            "AppSecretKey": settings.CAPTCHA_APP_SECRET,
            "NeedGetCaptchaTime": 1,
        }

        # verify
        try:
            req = models.DescribeCaptchaResultRequest()
            req.from_json_string(json.dumps(params))
            resp = self._client.DescribeCaptchaResult(req)
            resp = json.loads(resp.to_json_string())
            is_valid = resp.get("CaptchaCode") == CaptchaResultCode.OK and (
                resp.get("EvilLevel") is None or resp.get("EvilLevel") == EvilLevel.LOW
            )
        except TencentCloudSDKException as err:
            is_valid = False
            resp = {
                "code": err.get_code(),
                "message": err.get_message(),
                "request_id": err.get_request_id(),
                "GetCaptchaTime": int(datetime.datetime.now().timestamp()),
            }

        logger.info("[TCaptchaVerifyResult] Request: %s; Params: %s; Result: %s", self.kwargs, params, resp)
        return is_valid
