from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BoothViewSet

router = DefaultRouter()
router.register(r'booths', BoothViewSet, basename='booth')

urlpatterns = [
    path('', include(router.urls)),
]