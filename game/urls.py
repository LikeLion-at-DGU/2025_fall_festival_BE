from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import gameViewset

router = DefaultRouter()
router.register(r'games', gameViewset, basename='games')

urlpatterns = [
    path('', include(router.urls)),
]