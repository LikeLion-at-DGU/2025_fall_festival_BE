from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TranslationViewSet

router = DefaultRouter()
router.register(r"translations", TranslationViewSet, basename="translation")

urlpatterns = [
    path("", include(router.urls)),
]
