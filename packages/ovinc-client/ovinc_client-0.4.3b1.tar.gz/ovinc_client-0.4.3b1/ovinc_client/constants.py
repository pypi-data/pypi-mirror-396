import enum

from pydantic import BaseModel as BaseDataModel
from pydantic import Field

# Client
OVINC_CLIENT_SIGNATURE = "OVINC Client"
OVINC_CLIENT_TIMEOUT = 60

# App Auth
APP_AUTH_HEADER_APPID_KEY = "ovinc-appid"
APP_AUTH_HEADER_APPID_SIGN = "ovinc-sign"
APP_AUTH_HEADER_APPID_TIMESTAMP = "ovinc-timestamp"
APP_AUTH_HEADER_APPID_NONCE = "ovinc-nonce"


# Request
class RequestMethodEnum(enum.Enum):
    GET = "GET"
    POST = "POST"


class ResponseData(BaseDataModel):
    result: bool
    data: dict = Field(default=dict)
