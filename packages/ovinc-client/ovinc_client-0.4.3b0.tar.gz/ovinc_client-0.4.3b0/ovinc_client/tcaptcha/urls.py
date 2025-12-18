from rest_framework.routers import DefaultRouter

from ovinc_client.tcaptcha.views import CaptchaViewSet

router = DefaultRouter()
router.register("", CaptchaViewSet, basename="captcha")

urlpatterns = router.urls
