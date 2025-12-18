import base64
import datetime

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from django.conf import settings
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from ovinc_client.core.auth import SessionAuthenticate
from ovinc_client.core.utils import uniq_id_without_time
from ovinc_client.core.viewsets import MainViewSet


class CaptchaViewSet(MainViewSet):
    """
    Captcha
    """

    @action(methods=["GET"], detail=False, authentication_classes=[SessionAuthenticate])
    def config(self, request: Request, *args, **kwargs) -> Response:
        """
        Captcha Config
        """

        # encrypt app id
        nonce = uniq_id_without_time()[:16].encode()
        cipher = AES.new((settings.CAPTCHA_APP_SECRET * 2)[:32].encode(), AES.MODE_CBC, nonce)
        plain_text = (
            f"{settings.CAPTCHA_APP_ID}&{int(datetime.datetime.now().timestamp())}&{settings.CAPTCHA_APP_INFO_TIMEOUT}"
        )
        cipher_text = cipher.encrypt(pad(plain_text.encode(), AES.block_size))
        aid_encrypted = base64.b64encode(nonce + cipher_text).decode()

        # response
        return Response(
            data={
                "is_enabled": settings.CAPTCHA_ENABLED,
                "app_id": settings.CAPTCHA_APP_ID,
                "aid_encrypted": aid_encrypted,
            }
        )
