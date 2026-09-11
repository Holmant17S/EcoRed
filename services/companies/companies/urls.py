from django.urls import include, path
from rest_framework.routers import DefaultRouter

from companies.views import CompanyViewSet, health

router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="companies")

urlpatterns = [
    path("health/", health),
    path("", include(router.urls)),
]
