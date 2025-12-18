from ovinc_client.components.base import Component, Endpoint
from ovinc_client.constants import RequestMethodEnum


class Auth(Component):
    """
    Auth
    """

    def __init__(self, client, base_url: str):
        self.verify_code = VerifyCodeEndpoint(client, base_url)


class VerifyCodeEndpoint(Endpoint):
    """
    Send Mail
    """

    method = RequestMethodEnum.POST.value
    path = "/account/verify_code/"
