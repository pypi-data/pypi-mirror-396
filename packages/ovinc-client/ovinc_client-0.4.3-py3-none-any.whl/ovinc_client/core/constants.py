from django.utils.translation import gettext_lazy

from ovinc_client.core.models import TextChoices

# Char Length
SMS_CHAR_LENGTH = 12
SHORT_CHAR_LENGTH = 32
MEDIUM_CHAR_LENGTH = 64
MAX_CHAR_LENGTH = 255
PHONE_NUMBER_CHAR_LENGTH = 11
VERIFY_CODE_LENGTH = 6

# Pagination
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# Cache
DEFAULT_CACHE_TIMEOUT = 60

# SLEEP
TASK_RETRY_DEFAULT_SLEEP_TIME = 60


# Request
class ViewActionChoices(TextChoices):
    LIST = "list", gettext_lazy("LIST")
    CREATE = "create", gettext_lazy("CREATE")
    UPDATE = "update", gettext_lazy("UPDATE")
    PARTIAL_UPDATE = "partial_update", gettext_lazy("PARTIAL_UPDATE")
    DESTROY = "destroy", gettext_lazy("DESTROY")
