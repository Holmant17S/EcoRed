from django.urls import include, path
from rest_framework.routers import DefaultRouter

from materials.views import MaterialListingViewSet, health

router = DefaultRouter()
router.register(r"materials", MaterialListingViewSet, basename="materials")

urlpatterns = [
    path("health/", health),
    path("", include(router.urls)),
]
