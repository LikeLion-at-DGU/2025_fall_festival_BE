from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import gameViewset

router = DefaultRouter()
router.register(r'game', gameViewset, basename='game')

urlpatterns = [
    path('', include(router.urls)),
]