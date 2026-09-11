from django.urls import include, path
from rest_framework.routers import DefaultRouter

from solicitudes.views import MaterialRequestViewSet, health

router = DefaultRouter()
router.register(r"requests", MaterialRequestViewSet, basename="requests")

urlpatterns = [
    path("health/", health),
    path("", include(router.urls)),
]
