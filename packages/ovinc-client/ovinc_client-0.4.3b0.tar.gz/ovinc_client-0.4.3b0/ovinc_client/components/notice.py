from ovinc_client.components.base import Component, Endpoint
from ovinc_client.constants import RequestMethodEnum


class Notice(Component):
    """
    Notice
    """

    def __init__(self, client, base_url: str):
        self.mail = MailEndpoint(client, base_url)
        self.sms = SMSEndpoint(client, base_url)
        self.robot = RobotEndpoint(client, base_url)


class MailEndpoint(Endpoint):
    """
    Send Mail
    """

    method = RequestMethodEnum.POST.value
    path = "/notice/mail/"


class RobotEndpoint(Endpoint):
    """
    Send Robot Msg
    """

    method = RequestMethodEnum.POST.value
    path = "/notice/robot/"


class SMSEndpoint(Endpoint):
    """
    Send SMS
    """

    method = RequestMethodEnum.POST.value
    path = "/notice/sms/"
