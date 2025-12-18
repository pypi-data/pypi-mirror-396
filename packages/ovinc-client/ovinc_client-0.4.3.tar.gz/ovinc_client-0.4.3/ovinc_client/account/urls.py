from rest_framework.routers import DefaultRouter

from ovinc_client.account.views import UserInfoViewSet, UserSignViewSet

router = DefaultRouter()
router.register("", UserSignViewSet)
router.register("user_info", UserInfoViewSet, basename="user_info")

urlpatterns = router.urls
