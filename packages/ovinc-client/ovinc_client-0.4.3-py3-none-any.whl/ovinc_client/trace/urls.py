from rest_framework.routers import DefaultRouter

from ovinc_client.trace.views import RUMViewSet

router = DefaultRouter()
router.register("rum", RUMViewSet, basename="rum")

urlpatterns = router.urls
