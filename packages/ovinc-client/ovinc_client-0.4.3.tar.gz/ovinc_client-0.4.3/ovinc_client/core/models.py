from types import DynamicClassAttribute

from django.db import models
from django.db.models import CharField
from django.db.models import ForeignKey as _ForeignKey
from django.db.models import IntegerChoices as _IntegerChoices
from django.db.models import ManyToManyField as _ManyToManyField
from django.db.models import QuerySet
from django.db.models import TextChoices as _TextChoices
from django.utils.translation import gettext_lazy
from rest_framework.request import Request as _Request

from ovinc_client.core.utils import uniq_id_without_time


class Empty:
    ...


class IntegerChoices(_IntegerChoices):
    """
    Int Choices
    """

    @DynamicClassAttribute
    def value(self) -> int:
        """
        Get choice value
        """

        return self._value_


class TextChoices(_TextChoices):
    """
    Text Choices
    """

    @DynamicClassAttribute
    def value(self) -> str:
        """
        Get choice value
        """

        return self._value_


class UniqIDField(CharField):
    def __init__(self, verbose_name, **kwargs):
        # pylint: disable=R0401,C0415
        from ovinc_client.core.constants import SHORT_CHAR_LENGTH

        kwargs.update({"primary_key": True, "max_length": SHORT_CHAR_LENGTH, "default": uniq_id_without_time})
        super().__init__(verbose_name, **kwargs)


class ForeignKey(_ForeignKey):
    """
    ForeignKey
    """

    # pylint: disable=R0913,R0917
    def __init__(
        self,
        verbose_name: str,
        to: str,
        on_delete: callable,
        related_name: str = None,
        related_query_name: str = None,
        db_constraint: str = False,
        **kwargs,
    ):
        super().__init__(
            to=to,
            on_delete=on_delete,
            related_name=related_name,
            related_query_name=related_query_name,
            db_constraint=db_constraint,
            verbose_name=verbose_name,
            **kwargs,
        )


class ManyToManyField(_ManyToManyField):
    """
    ManyToManyField
    """

    # pylint: disable=R0913,R0917
    def __init__(
        self,
        verbose_name: str,
        to: str,
        related_name: str = None,
        related_query_name: str = None,
        db_constraint: bool = False,
        **kwargs,
    ):
        super().__init__(
            verbose_name=verbose_name,
            to=to,
            related_name=related_name,
            related_query_name=related_query_name,
            db_constraint=db_constraint,
            **kwargs,
        )


class BaseModel(models.Model):
    """
    Base Model
    """

    objects = models.Manager()

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.pk

    @classmethod
    def get_queryset(cls) -> QuerySet:
        return cls.objects.all()

    def get_name(self) -> str:
        return str(self)


class SoftDeletedManager(models.Manager):
    """
    Soft Delete Model Manager
    """

    def get(self, *args, **kwargs) -> "SoftDeletedModel":
        kwargs = self._add_soft_delete_param(kwargs)
        return super().get(*args, **kwargs)

    def filter(self, *args, **kwargs) -> QuerySet:
        kwargs = self._add_soft_delete_param(kwargs)
        return super().filter(*args, **kwargs)

    def all(self) -> QuerySet:
        return self.filter()

    def _add_soft_delete_param(self, kwargs) -> dict:
        return {**kwargs, "is_deleted": False}


class SoftDeletedModel(BaseModel):
    """
    Soft Delete Model
    """

    is_deleted = models.BooleanField(gettext_lazy("Soft Delete"), default=False, db_index=True)

    objects = SoftDeletedManager()
    _objects = models.Manager()

    class Meta:
        abstract = True

    @classmethod
    def get_queryset(cls) -> QuerySet:
        return cls.objects.filter(is_deleted=False)

    def delete(self, *args, **kwargs) -> None:
        self.is_deleted = True
        self.save()


class RequestMock(_Request):
    """
    Mock for Request
    """

    def __init__(self, user, params: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_query_params = params
        self._init_data = params
        self._init_user = user

    @property
    def user(self):
        return self._init_user

    @property
    def query_params(self) -> dict:
        return self._init_query_params

    @property
    def data(self) -> dict:
        return self._init_data
