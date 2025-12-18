import datetime

from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone

from ovinc_client.account.models import UserToken
from ovinc_client.core.utils import get_ip


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    # pylint: disable=E1101
    UserToken.objects.create(
        user=user,
        session_key=request.session.session_key,
        cache_key=request.session.cache_key,
        login_ip=get_ip(request),
        user_agent=request.headers.get("User-Agent"),
        expired_at=timezone.now() + datetime.timedelta(seconds=settings.SESSION_COOKIE_AGE),
    )


@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    # pylint: disable=E1101
    (
        UserToken.objects.filter(user=user)
        .filter(session_key=request.session.session_key)
        .filter(expired_at__gte=timezone.now())
    ).update(expired_at=timezone.now())
