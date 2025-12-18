from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class AccountConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ovinc_client.account"
    verbose_name = gettext_lazy("User Account")

    def ready(self):
        # pylint: disable=C0415,W0611
        import ovinc_client.account.signals  # noqa
