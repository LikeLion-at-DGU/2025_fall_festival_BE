from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameViewset

router = DefaultRouter()
router.register(r'games', GameViewset, basename='games')

urlpatterns = [
    path('', include(router.urls)),
]