import abc

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, AnonymousUser, PermissionsMixin
from django.contrib.auth.models import UserManager as _UserManager
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext, gettext_lazy

from ovinc_client.account.constants import UserTypeChoices
from ovinc_client.core.constants import (
    MAX_CHAR_LENGTH,
    MEDIUM_CHAR_LENGTH,
    SHORT_CHAR_LENGTH,
)
from ovinc_client.core.models import SoftDeletedManager, SoftDeletedModel


class UserManager(SoftDeletedManager, _UserManager):
    """
    User Manager
    """

    # pylint: disable=W0237
    def create_user(self, username, nick_name=None, password=None, **extra_fields):
        if not username:
            raise ValueError(gettext("Username Cannot be Empty"))
        user = self.model(username=username, nick_name=nick_name, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    # pylint: disable=W0237
    def create_superuser(self, username, nick_name=None, password=None, **extra_fields):
        extra_fields["is_superuser"] = True
        self.create_user(username, nick_name, password, **extra_fields)


class User(SoftDeletedModel, AbstractBaseUser, PermissionsMixin):
    """
    User
    """

    username = models.CharField(
        gettext_lazy("username"),
        max_length=SHORT_CHAR_LENGTH,
        primary_key=True,
        validators=[AbstractUser.username_validator],
        error_messages={"unique": gettext_lazy("already in use")},
    )
    nick_name = models.CharField(gettext_lazy("Nick Name"), max_length=SHORT_CHAR_LENGTH, blank=True, null=True)
    user_type = models.CharField(
        gettext_lazy("User Type"),
        choices=UserTypeChoices.choices,
        max_length=SHORT_CHAR_LENGTH,
        default=UserTypeChoices.PERSONAL.value,
    )
    date_joined = models.DateTimeField(gettext_lazy("Date Joined"), auto_now_add=True)
    is_staff = models.BooleanField(gettext_lazy("Is Staff"), default=False)

    USERNAME_FIELD = "username"
    objects = UserManager()
    _objects = _UserManager()

    class Meta:
        verbose_name = gettext_lazy("User")
        verbose_name_plural = verbose_name
        ordering = ["username"]

    def logout_all(self) -> None:
        """
        Logout all token
        """

        # pylint: disable=E1101
        tokens = UserToken.objects.filter(user=self, expired_at__gte=timezone.now())
        for token in tokens:
            cache.delete(token.cache_key)
        tokens.update(expired_at=timezone.now())


class CustomAnonymousUser(AnonymousUser, abc.ABC):
    """
    Anonymous User
    """

    nick_name = "AnonymousUser"
    user_type = UserTypeChoices.PLATFORM.value


class UserToken(models.Model):
    """
    User Token
    """

    id = models.BigAutoField(gettext_lazy("ID"), primary_key=True)
    user = models.ForeignKey(
        verbose_name=gettext_lazy("User"), to="User", on_delete=models.PROTECT, db_constraint=False
    )
    session_key = models.CharField(gettext_lazy("Session Key"), max_length=MAX_CHAR_LENGTH, db_index=True)
    cache_key = models.CharField(gettext_lazy("Cache Key"), max_length=MAX_CHAR_LENGTH, db_index=True)
    login_ip = models.CharField(gettext_lazy("Login IP"), max_length=MEDIUM_CHAR_LENGTH, db_index=True)
    user_agent = models.TextField(gettext_lazy("User Agent"), null=True, blank=True)
    expired_at = models.DateTimeField(gettext_lazy("Expired at"), db_index=True)

    class Meta:
        verbose_name = gettext_lazy("User Token")
        verbose_name_plural = verbose_name
        ordering = ["-id"]
        index_together = [
            ["user", "expired_at"],
            ["user", "session_key", "expired_at"],
        ]
